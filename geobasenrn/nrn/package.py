"""Create distributable files of NRN data."""

import click
import fiona
import geobasenrn as nrn
import geobasenrn.io as nrnio
from geobasenrn.nrn import options
from geobasenrn.schema import schema
import geopandas as gpd
import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
from tqdm import tqdm
import zipfile

# Make sure GDAL/OGR is available
try:
    from osgeo import ogr, osr
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

logger = logging.getLogger(__name__)

# By default OGR will not throw exceptions, which can make problem detection harder. This tells OGR to always 
# raise exceptions.
ogr.UseExceptions()

# The name of the driver to use when creating output
ogr_drivers = {
    'gpkg': 'GPKG',
    'shp': 'Esri Shapefile',
    'gml': 'GML',
    'kml': 'KML'
}

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
    format_driver = ogr_drivers.get(output_format)
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
                        create_layer(data_source, tbl, layer_name, output_format, lang)
                        # Write the data to the new layer
                        write_data_output(dframes[layer_key], layer_name, data_source, output_format, lang)

                        # Release the Shapefile pointer to let go of the file handle
                        if output_format == 'shp':
                            data_source = None

                # Release the GPKG pointer to let go of the file handle
                data_source = None

            elif output_format == 'gml':
                # Create a GML file for each layer. GML files live within a parent folder named after their 
                # language.
                folder_name  = nrnio.get_gml_filename('GML', pt_identifier, major_version, minor_version, lang)[:-4]
                folder_path = Path(temp_dir).joinpath(folder_name_en)
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
                        create_layer(data_source, tbl, layer_name, output_format, lang)
                        # Write the data to the new layer
                        write_data_output(dframes[layer_key], layer_namee, data_sourcee, output_format, lang)

                        # Release the GML pointers to let go of the file handle
                        data_source = None

        # Compress the data and delivery it to the desired output folder
        temp_path = Path(temp_dir)
        if compress:
            logger.debug("Asked for data compression. Building zip file.")
            # Get an output compliant filename
            zip_name = 'output.zip'
            if output_format == 'gpkg' or output_format == 'shp':
                fname_function = f'get_{output_format}_filename'
                format_fname = Path(getattr(nrnio, fname_function)(pt_identifier,
                                                                   major_version,
                                                                   minor_version,
                                                                   lang_en))
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

def create_layer(data_source: ogr.DataSource, tbl, layer_name: str, output_format: str, lang: str='en'):
    """Create a layer within the data source that conforms to output format specifications."""
    logger.debug("Creating %s layer for %s", output_format, tbl.__class__.__name__)

    if data_source == None:
        raise ValueError('Invalid data source provided')

    # Define the SRS for output data
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(nrn.SRS_EPSG_CODE)
    # Don't define a spatial reference on data with no shape.
    if tbl.shape_type == ogr.wkbNone:
        srs = None

    # Create the layer
    logger.debug("Creating layer with name %s in %s", layer_name, data_source.GetName())
    layer = data_source.CreateLayer(layer_name, srs, tbl.shape_type)

    # Set the field names to match what is expected for the language
    logger.debug("Creating %s fields", lang)
    for field in tbl.fields:
        name = schema[field][output_format][lang]
        field_type = schema[field]['type']
        width = schema[field]['width']

        # Create a field definiton object.
        field_defn = ogr.FieldDefn(name, field_type)
        field_defn.SetWidth(width)
        # Create the field on the layer.
        layer.CreateField(field_defn)

def write_data_output(df, layer_name: str, data_source: ogr.DataSource, output_format: str, lang: str='en'):
    """Write the contents of dframes out to output format in the specified work directory.
    
    This creates either a French or English copy of the data, based on the supplied language.
    """
    logger.debug("Writing %s data to %s", layer_name, data_source.GetName())
    
    # Map the column names in the dataframe to the appropriate language.
    # Build a name map for field names
    logger.debug("Creating column map from %s schema", lang)
    column_map = {}
    for col_name in schema:
        column_map[col_name] = schema[col_name][output_format][lang]
    
    # Rename all the columns in each dataframe.
    logger.debug("Naming columns for %s", layer_name)
    df = df.rename(columns=column_map)
    
    # Dump the data to the corresponding table, using append since a skeleton table already exists.
    format_driver = ogr_drivers.get(output_format)
    # The preferred way to do this would be with a call to geopandas .to_file(), but there is a bug in v0.7 that 
    # prevents appending data to an existing schema.
    # df.to_file(out_path, layer=layer_name, driver=format_driver, mode="a", index=False)

    # Get the layer within the datasource
    logger.debug("Getting reference to layer %s in data source", layer_name)
    # Some data sources don't use named layers and only have one layer
    if data_source.GetLayerCount() == 1:
        layer = data_source.GetLayerByIndex(0)
    else:
        layer = data_source.GetLayerByName(layer_name)

    # Determine if this is a geometry or attribute layer, and write as appropriate
    if type(df) is gpd.GeoDataFrame:
        write_geom_layer(df, layer)
    else:
        write_attr_layer(df, layer)

def write_geom_layer(df, layer: ogr.Layer):
    """Write a GeoDataFrame to a layer."""
    # Iterate each feature in the dataframe and write it to the layer. This will produce a __geo_interface__ compliant
    # dictionary that can be used to get at the records.
    layer_name = layer.GetName()
    logger.debug("Iterating features in the GeoDataFrame and writing to the layer.")
    for feat in tqdm(df.iterfeatures(), total=len(df), desc=f'Writing {layer_name}'):
        # Separate the geometry from the properties to make working with it easier.
        geom_json = json.dumps(feat['geometry'])
        feature_properties = feat['properties']

        # Instantiate a new feature
        feature = ogr.Feature(layer.GetLayerDefn())

        # Iterate all of the properties and add them to the feature.
        for prop in feature_properties:
            # logger.debug("Setting %s=%s", prop, feature_properties[prop])
            feature.SetField(prop, feature_properties[prop])
        
        geom = ogr.CreateGeometryFromJson(geom_json)
        feature.SetGeometry(geom)

        # Save the feature to the layer
        layer.CreateFeature(feature)

        # Clear the pointer before moving on to the next feature
        feature = None

def write_attr_layer(df, layer: ogr.Layer):
    """Write a DataFrame to a layer."""
    # Iterate each feature in the dataframe and write it to the layer. This will produce a __geo_interface__ compliant
    # dictionary that can be used to get at the records.
    layer_name = layer.GetName()
    logger.debug("Iterating features in the DataFrame and writing to the layer.")
    for row in tqdm(df.itertuples(index=False), total=len(df), desc=f'Writing {layer_name}'):
        # OGR will write one field at a time, so make a dictionary to iterate through the keys
        feature_properties = row._asdict()

        # Instantiate a new feature
        feature = ogr.Feature(layer.GetLayerDefn())

        # iterate every field to create a new feature
        for prop in feature_properties:
            # skip fields that are managed by the layer itself
            if prop in ('id', 'geom'):
                continue
            # logger.debug("Setting %s=%s", prop, feature_properties[prop])
            feature.SetField(prop, feature_properties[prop])

        # Save the feature to the layer
        layer.CreateFeature(feature)

        # Clear the pointer before moving on to the next feature
        feature = None
