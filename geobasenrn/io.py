"""Definitions for valid layers within the GPKG."""

import fiona
import geopandas as gpd
import logging
import osgeo.ogr as ogr
import pandas as pd
from pathlib import Path
import requests
import sqlite3
import tempfile
import zipfile

logger = logging.getLogger(__name__)

def compress(inpath: Path, outfile: Path = None) -> None:
    """Given a directory or file path, create a zip compressed version of it.

    If the outfile path does not contain a .zip extension, one is added.
    """
    # Do not try to compress an existing archive.
    if zipfile.is_zipfile(inpath):
        return None

    # If no output file was provided, use the path of the input file
    if not outfile:
        name = f'{inpath.name}.zip'
        outfile = inpath.parent.joinpath(name)

    # Check if the output is valid
    # TODO: This is a crude check that can still end up creating invalid names.
    if not outfile.name.endswith('.zip'):
        outfile.name = f'{outfile.name}.zip'
    
    # Write all of the contents of the input to the zip archive
    try:
        with zipfile.ZipFile(outfile, 'w') as archive:
            for item in inpath.rglob('*'):
                archive.write(item)
    except (zipfile.BadZipFile, zipfile.LargeZipFile) as err:
        logger.exception("Unable to create zip archive.")
        raise err

def df_to_gpkg(gpkg: Path, df: pandas.DataFrame, table_name: str)
    """Write a non-spatial DataFrame to a GeoPackage file."""
    try:
        # create a connection to the sqlite file
        con = sqlite3.connect(output_path)

        # Write to GeoPackage.
        df.to_sql(table_name, con, if_exists="replace", index=False)

        # Add metedata record to gpkg_contents.
        sql = "INSERT OR IGNORE INTO gpkg_contents (table_name, data_type) VALUES (?,?)"
        con.cursor().execute(sql, (table_name, 'attributes'))
        con.commit()
        con.close()
    except sqlite3.Error as err:
        logger.exception(f"Unable to write to {gpkg}")
        raise err
    
def get_url(url, max_attempts=10, **kwargs):
    """Attempts to retrieve a url."""
    # how long to wait between failed attempts
    seconds_between_attempts = 5

    for attempt in range(max_attempts):
        try:
            logger.debug("Connecting to url (attempt %s of %s): %s", attempt, max_attempts, url)

            # Get url response.
            response = requests.get(url, **kwargs)
            return response
        except (TimeoutError, requests.exceptions.RequestException) as err:
            if attempt < max_attempts:
                logger.exception("Failed to retrieve file within %s attempts: %s", max_attempts, err)
                raise err
            else:
                logger.warning("Failed to get url response. Retrying...")
                time.sleep(seconds_between_attempts)

def get_gpkg_contents(gpkg_path: Path) -> dict:
    """Load the entire contents of a GeoPackage into DataFrames so that they can be processed further.

    This will create either a GeoDataFrame or a DataFrame, depending on if the layer in the GPKG file has a
    spatial column or not.
    """
    # Each layer will be keyed by name.
    dframes = dict()

    # Layers to look for within a dataset.
    spatial_layers = ['blkpassage', 'ferryseg', 'junction', 'roadseg', 'tollpoint']
    attribute_layers = ['addrange', 'altnamlink', 'strplaname']

    # Get a list of layers within the GPKG file
    existing_layers = fiona.listlayers(gpkg_path)

    # Look for matches, and store the layer as a DataFrame. Layer names in geopackages have names that include their
    # version information. The name is always at the end though.
    for layer_name in spatial_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                dframes[layer_name] = gpd.read_file(gpkg_path, layer=gpkg_layer)

    for layer_name in attribute_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()

        try:
            # Create sqlite connection.
            conn = sqlite3.connect(gpkg_path)
            
            # Check each existing layer
            for gpkg_layer in existing_layers:
                if gpkg_layer.endswith(layer_slug):
                    dframes[layer_name] = pd.read_sql_table(gpkg_layer, con=conn, coerce_float=False)
            
            conn.close()
        except sqlite3.Error as err:
            logger.exception("Unable to load GPKG attribute tables from: %s", gpkg_path)
            raise err
    
    # Generate a warning for every table that could not be found.
    for layer in (spatial_layers + attribute_layers):
        if layer not in dframes:
            logger.warning("Layer not found: %s", layer)
    
    # Return everything that was found.
    return dframes

def get_valid_layer_name(slug: str, identifier: str, major: int, minor: int, lang: str='en') -> str:
    """Generate a valid layer name to be used in layered datasets.
    
    At the moment supported layered datasets are GPKG and SHP.
    """
    layer_name = ''

    # If the slug or identifier are not valid strings an exception would be thrown.
    if type(slug) is not str:
        slug = str(slug)
    if type(identifier) is not str:
        identifier = str(identifier)

    # Generate the layer name.
    if lang='en':
        layer_name = f'NRN_{identifier.upper()}_{major}_{minor}_{slug.upper()}'
    elif lang='fr':
        layer_name = f'RRN_{identifier.upper()}_{major}_{minor}_{slug.upper()}'
    
    return layer_name


# Base class for layers in a dataset to provide common bits of functionality.
class BaseTable:
    """A base class to provide some common functions for all layers.

    This class is not meant to be used directly.
    """
    pass

# Field definitions found in the different tables in each dataset.

class AddressRangeTable(BaseTable):
    """Definition of the address range table."""

    def __init__(self):
        name_en = 'addrange'
        name_fr = 'INTERVADR'
        fields = {
            "acqtech": ogr.FieldDefn("ACQTECH", ogr.OFTString),
            "metacover": ogr.FieldDefn("METACOVER", ogr.OFTString),
            "credate": ogr.FieldDefn("CREDATE", ogr.OFTDate),
            "datasetnam": ogr.FieldDefn("DATASETNAM", ogr.OFTString),
            "accuracy": ogr.FieldDefn("ACCURACY"),
            "provider": ogr.FieldDefn("PROVIDER"),
            "revdate": ogr.FieldDefn("REVDATE", ogr.OFTDate),
            "specvers": ogr.FieldDefn("SPECVERS", ogr.OFTReal),
            "l_altnamnid": ogr.FieldDefn("L_ALTNANID", ogr.OFTString),
            "r_altnamnid": ogr.FieldDefn("R_ALTNANID", ogr.OFTString),
            "l_digdirfg": ogr.FieldDefn("L_DIGDIRFG", ogr.OFTString),
            "r_digdirfg": ogr.FieldDefn("R_DIGDIRFG", ogr.OFTString),
            "l_hnumf": ogr.FieldDefn("L_HNUMF", ogr.OFTString),
            "r_hnumf": ogr.FieldDefn("R_HNUMF", ogr.OFTString),
            "l_hnumsuff": ogr.FieldDefn("L_HNUMSUFF", ogr.OFTString),
            "r_hnumsuff": ogr.FieldDefn("R_HNUMSUFF", ogr.OFTString),
            "l_hnumtypf": ogr.FieldDefn("L_HNUMTYPF", ogr.OFTString),
            "r_hnumtypf": ogr.FieldDefn("R_HNUMTYPF", ogr.OFTString),
            "l_hnumstr": ogr.FieldDefn("L_HNUMSTR", ogr.OFTString),
            "r_hnumstr": ogr.FieldDefn("R_HNUMSTR", ogr.OFTString),
            "l_hnuml": ogr.FieldDefn("L_HNUML", ogr.OFTString),
            "r_hnuml": ogr.FieldDefn("R_HNUML", ogr.OFTString),
            "nid": ogr.FieldDefn("NID", ogr.OFTString),
            "l_hnumsufl": ogr.FieldDefn("L_HNUMSUFL", ogr.OFTString),
            "r_hnumsufl": ogr.FieldDefn("R_HNUMSUFL", ogr.OFTString),
            "l_hnumtypl": ogr.FieldDefn("L_HNUMTYPL", ogr.OFTString),
            "r_hnumtypl": ogr.FieldDefn("R_HNUMTYPL", ogr.OFTString),
            "l_offnanid": ogr.FieldDefn("L_OFFNANID", ogr.OFTString),
            "r_offnanid": ogr.FieldDefn("R_OFFNANID", ogr.OFTString),
            "l_rfsysind": ogr.FieldDefn("L_RFSYSIND", ogr.OFTString),
            "r_rfsysind": ogr.FieldDefn("R_RFSYSIND", ogr.OFTString)
        }
    
    def _set_field_widths(self):
        """Set the width of each field in the table."""
        #example
        self.fields['acqtech'].SetWidth(24)
    
    def get_gpkg_name(self, source, major, minor, lang='en'):
        """Generate a valid layer name to be used in GPKG outputs."""
        if lang == 'en':
            slug = self.name_en
        else:
            slug = self.name_fr

        name = get_valid_layer_name(slug, source, major, minor, lang)
        return name
    
        

# Common fields
nid_field = ogr.FieldDefn("NID", ogr.OFTString)
datasetnam_field = ogr.FieldDefn("DATASETNAM", ogr.OFTString)
credate_field = ogr.FieldDefn("CREDATE", ogr.OFTDate)
revdate_field = ogr.FieldDefn("REVDATE", ogr.OFTDate)
specvers_field = ogr.FieldDefn("SPECVERS", ogr.OFTReal)
acqtech_field = ogr.FieldDefn("ACQTECH", ogr.OFTString)
