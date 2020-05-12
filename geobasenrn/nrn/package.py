"""Create distributable files of NRN data."""

import click
import geobasenrn as nrn
import geobasenrn.io as nrnio
from geobasenrn.nrn import options
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

# Make sure GDAL/OGR is available
try:
    from osgeo import ogr, osr
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

logger = logging.getLogger(__name__)

@click.command(short_help="Create distributable NRN data.")
@options.precision_opt
@click.option('-i', '--input', 'infile',
              type=click.Path(dir_okay=False, file_okay=True,
                              resolve_path=True),
              required=True,
              help="Directory of where to write the file.")
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

    # The name of the driver to use when creating output
    ogr_drivers = {
        'gpkg': 'GPKG',
        'shp': 'Esri Shapefile',
        'gml': 'GML',
        'kml': 'KML'
    }
    format_driver = ogr_drivers.get(output_format)
    logger.debug("Chosen output driver: %s", format_driver)

    # Create a temporary workspace within which to create all the data.
    with tempfile.TemporaryDirectory() as temp_dir:
        lang_en = 'en'
        lang_fr = 'fr'

        # Process outputs for GPKG format
        if output_format == 'gpkg':
            logger.debug("GPKG output format selected. Building products.")
            driver = ogr.GetDriverByName(format_driver)

            # Get a proper output file name.
            fname_en = nrnio.get_gpkg_filename(pt_identifier, major_version, minor_version, lang_en)
            out_path_en = Path(temp_dir).joinpath(fname_en)
            logger.debug("English file name: %s", fname_en)
            fname_fr = nrnio.get_gpkg_filename(pt_identifier, major_version, minor_version, lang_fr)
            out_path_fr = Path(temp_dir).joinpath(fname_fr)
            logger.debug("French file name: %s", fname_fr)

            # Create the empty GeoPackage for data to be loaded in to.
            logger.debug("Creating English and French data files.")
            # OGR doesn't understand pathlib paths, so force posix paths
            data_source_en = driver.CreateDataSource(out_path_en.as_posix())
            data_source_fr = driver.CreateDataSource(out_path_fr.as_posix())

            # Find out which layers are present in the DataFrames and create those layers
            if 'addrange' in dframes:
                logger.debug("Building addrange tables.")
                tbl = nrnio.AddressRangeTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'altnamlink' in dframes:
                logger.debug("Building altnamlink tables.")
                tbl = nrnio.AlternateNameLinkTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'blkpassage' in dframes:
                logger.debug("Building blkpassage tables.")
                tbl = nrnio.BlockedPassageTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'ferryseg' in dframes:
                logger.debug("Building ferryseg tables.")
                tbl = nrnio.FerrySegmentTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'junction' in dframes:
                logger.debug("Building junction tables.")
                tbl = nrnio.JunctionTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'roadseg' in dframes:
                logger.debug("Building roadseg tables.")
                tbl = nrnio.RoadSegmentTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'strplaname' in dframes:
                logger.debug("Building strplaname tables.")
                tbl = nrnio.StreetPlaceNameTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)
            if 'tollpoint' in dframes:
                logger.debug("Building tollpoint tables.")
                tbl = nrnio.TollPointTable()
                create_gpkg_layer(data_source_en, tbl, pt_identifier, major_version, minor_version, lang_en)
                create_gpkg_layer(data_source_fr, tbl, pt_identifier, major_version, minor_version, lang_fr)

            # Write the data to the GPKG.
            write_gpkg_output(dframes, out_path_en, lang_en)
            write_gpkg_output(dframes, out_path_fr, lang_fr)

            # release the OGR pointers to let go of the file handler
            data_source_en = None
            data_source_fr = None

        # Compress the data and delivery it to the desired output folder
        temp_path = Path(temp_dir)
        if compress:
            logger.debug("Asked for data compression. Building zip file.")
            # Get an output compliant filename
            zip_name = 'output.zip'
            if output_format == 'gpkg':
                format_fname = Path(nrnio.get_gpkg_filename(pt_identifier, major_version, minor_version, 'en'))
                # The gpkg name includes a language identifier on the stem. The zip file should include everything 
                # up to that point.
                zip_fname = f'{format_fname.stem[:-3]}.zip'
            
            # Compress the items found and write the output to where the user asked
            out_file = Path(out_path).joinpath(zip_fname)
            nrnio.compress(temp_path, out_file)
        else:
            logger.debug("No compression requested. Copying products to destination.")
            # no compress requested, so move the products directly to the output location
            artifacts = temp_path.glob('*')
            for item in artifacts:
                shutil.move(item, out_path)




    # TODO: Implement all the processing steps
    # Work should be done within a temporary directory to avoid any possible mixup with data in the current directory.
    # 1. Load the input data, which is the output of the conversion process after being validated
    # 2. Use OGR to build the layers for the chosen output format
    # 3. Output the data to the chosen format for English data
    # 4. Convert the intermediate data to French data
    # 5. Output the French data
    # 6. Compress the outputs
    

def create_gpkg_layer(data_source: ogr.DataSource, tbl, pt_ident: str, major: int, minor: int, 
                      lang: str='en'):
    """Create a layer within the data source that conforms to GeoPackage specifications."""
    logger.debug("Creating GPKG layer for %s", tbl.__class__.__name__)

    # Define the SRS for output data
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(nrn.SRS_EPSG_CODE)
    logger.debug("Spatial reference being used:\n%s", srs)

    # Create the layer
    layer_name = tbl.get_gpkg_layer_name(pt_ident, major, minor, lang)
    logger.debug("Creating layer with name %s", layer_name)
    layer = data_source.CreateLayer(layer_name, srs, tbl.shape_type)

    # Set the field names to match what is expected for the language
    logger.debug("Preparing field names for %s language", lang)
    tbl.set_gpkg_field_names(lang)

    # Create the fields in the layer
    for field in tbl.fields:
        logger.debug("Creating field %s on layer", field)
        layer.CreateField(tbl.fields[field])

def write_gpkg_output(dframes: dict, out_path: Path, lang: str='en') -> Path:
    """Write the contents of dframes out to GeoPackage in the specified work directory.
    
    This creates either a French or English copy of the data, based on the supplied language.
    """
    print(f"Writing DataFrames to {out_path} in language {lang}")
    