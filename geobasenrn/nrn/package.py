"""Create distributable files of NRN data."""

import click
import fiona
import geobasenrn as nrn
import geobasenrn.io as nrnio
from geobasenrn.nrn import options
from geobasenrn import schema
import geopandas as gpd
import logging
import numpy as np
from osgeo import ogr
import pandas as pd
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

logger = logging.getLogger(__name__)

# By default OGR will not throw exceptions, which can make problem detection harder. This tells OGR to always 
# raise exceptions.
ogr.UseExceptions()

# Map table short names to their matching class
class_map = schema.class_map

@click.command(short_help="Create distributable NRN data.")
@options.precision_opt
@click.option('-i', '--input', 'infile',
              type=click.Path(dir_okay=False, file_okay=True,
                              resolve_path=True),
              required=True,
              help="Path to the input GeoPackage.")
@click.option('-mjr',
              '--major-version',
              type=int,
              default=0,
              help="Major version of the data")
@click.option('-mnr',
              '--minor-version',
              type=int,
              default=0,
              help="Minor version of the data")
@click.option('-f', '--format', 'output_format',
              type=click.Choice(['gpkg', 'shp', 'gml', 'kml']),
              default='gpkg')
@click.option('-o', '--out-path',
              type=click.Path(dir_okay=True, file_okay=False,
                              resolve_path=True),
              default='.',
              help="Directory of where to write the file.")
@click.option('--compress/--no-compress',
              default=True,
              help="Compress the output into a zip archive.")
@click.pass_context
def package(ctx, precision, infile, major_version, minor_version,
            output_format, out_path, compress):
    """Create distributable files from NRN data.

    This is normally run against the output of the conversion command.
    """
    # Get which province or territory this is for.
    pt_identifier = ctx.obj['province_code']
    logger.debug("Identifier: %s", pt_identifier)

    # Retrieve the data from the conversion GPKG.
    logger.debug("Loading GPKG contents from %s", infile)
    dframes = nrnio.get_gpkg_contents(infile)

    # TODO: Add support for multiple formats to be specified in a single command
    format_driver = nrnio.ogr_drivers.get(output_format)
    logger.debug("Chosen output driver: %s", format_driver)
    # Driver to be used by OGR
    driver = ogr.GetDriverByName(format_driver)

    # Create a temporary workspace within which to create all the data.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Iterate over both languages to create the outputs for both
        output_languages = ('en', 'fr')
        for lang in output_languages:
            # Process outputs for the chosen format
            if output_format == 'gpkg' or output_format == 'shp':
                # GPKG has layers in a single file, so create that data source now
                if output_format == 'gpkg':
                    # Get a proper output file name.
                    fname = nrnio.get_gpkg_filename(pt_identifier, major_version, minor_version, lang)
                    out_path = Path(temp_dir).joinpath(fname)
                    logger.debug("File name for language %s: %s", lang, fname)

                    # Create the empty GeoPackage for data to be loaded in to.
                    logger.debug("Creating data files.")
                    # OGR doesn't understand pathlib paths, so force posix paths
                    data_source = driver.CreateDataSource(out_path.as_posix())

                # Layer name functions are based on the output format. This creates the right function name to call.
                layer_name_function = f'get_{output_format}_layer_name'
                # Create outputs for the data
                for layer_key in (nrn.spatial_layers + nrn.attribute_layers):
                    if layer_key in dframes:
                        logger.debug("Writing %s table", layer_key)

                        tbl = class_map[layer_key]
                        logger.debug("Creating layer from %s", tbl)
                        layer_name = getattr(nrnio, layer_name_function)(tbl, pt_identifier, major_version, minor_version, lang)

                        # shapefiles get a data source named after their layer names
                        if output_format == 'shp':
                            logger.debug("Creating shapefiles for %s", layer_key)
                            if tbl.shape_type == ogr.wkbNone:
                                file_extension = 'dbf'
                            else:
                                file_extension = 'shp'
                            out_path = Path(temp_dir).joinpath(f'{layer_name}.{file_extension}')
                            # OGR doesn't understand pathlib paths, so force posix paths
                            data_source = driver.CreateDataSource(out_path.as_posix())
                        
                        # Create the layer within the data source
                        nrnio.create_layer(data_source, tbl, layer_name, output_format, lang)
                        # Write the data to the new layer
                        nrnio.write_data_output(dframes[layer_key], layer_name, data_source, output_format, lang)

                        # Release the Shapefile pointer to let go of the file handle
                        if output_format == 'shp':
                            data_source = None

                # Release the GPKG pointer to let go of the file handle
                data_source = None

            elif output_format == 'gml':
                # Create a GML file for each layer. GML files live within a parent folder named after their 
                # language.
                folder_name  = nrnio.get_gml_filename('GML', pt_identifier, major_version, minor_version, lang)[:-4]
                folder_path = Path(temp_dir).joinpath(folder_name)
                # Create the folder to hold the files
                folder_path.mkdir()

                # Iterate the layers, writing each to a file
                for layer_key in (nrn.spatial_layers + nrn.attribute_layers):
                    if layer_key in dframes:
                        logger.debug("Writing %s to GML", layer_key)

                        tbl = class_map[layer_key]
                        layer_name = tbl.get_gml_layer_name(pt_identifier, major_version, minor_version, lang)
                        logger.debug("Layer name: %s", layer_name)
                        layer_path = folder_path.joinpath(layer_name)

                        # OGR doesn't understand pathlib paths, so force posix paths
                        data_source = driver.CreateDataSource(layer_path.as_posix())

                        # Create the layers within the GML files
                        nrnio.create_layer(data_source, tbl, layer_name, output_format, lang)
                        # Write the data to the new layer
                        nrnio.write_data_output(dframes[layer_key], layer_name, data_source, output_format, lang)

                        # Release the GML pointers to let go of the file handle
                        data_source = None

        # Compress the data and delivery it to the desired output folder
        temp_path = Path(temp_dir)
        if compress:
            logger.debug("Asked for data compression. Building zip file.")
            # Get an output compliant filename
            zip_fname = 'output.zip'
            if output_format == 'gpkg' or output_format == 'shp':
                fname_function = f'get_{output_format}_filename'
                format_fname = Path(getattr(nrnio, fname_function)(pt_identifier,
                                                                   major_version,
                                                                   minor_version,
                                                                   lang))
                zip_fname = format_fname.stem

                # The gpkg name includes a language identifier on the stem. The zip file should include everything 
                # up to that point.
                if output_format == 'gpkg':
                    zip_fname = format_fname.stem[:-3]
            elif output_format == 'gml':
                zip_fname == f'NRN_RRN_{pt_identifier.upper()}_{major_version}_{minor_version}_GML'
            
            # Compress the items found and write the output to where the user asked
            out_file = Path(out_path).joinpath(f'{zip_fname}.zip')
            nrnio.compress(temp_path, out_file)
        else:
            logger.debug("No compression requested. Copying products to destination.")
            # no compress requested, so move the products directly to the output location
            artifacts = temp_path.glob('*')
            for item in artifacts:
                shutil.move(item, out_path)
