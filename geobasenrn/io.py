"""Definitions for valid layers within an NRN dataset."""

import fiona
from geobasenrn import attribute_layers, spatial_layers
from geobasenrn.schema import schema
import geopandas as gpd
import logging
import osgeo.ogr as ogr
import pandas as pd
from pathlib import Path
import requests
import sqlite3
import tempfile
import warnings
import zipfile

logger = logging.getLogger(__name__)

def compress(inpath: Path, outfile: Path = None) -> None:
    """Given a directory or file path, create a zip compressed version of it.

    If the outfile path does not contain a .zip extension, one is added.
    """
    logger.debug("Compressing data in %s", inpath)
    # Do not try to compress an existing archive.
    if zipfile.is_zipfile(inpath):
        logger.warning("Input file is already compressed")
        return None

    # If no output file was provided, use the path of the input file
    if not outfile:
        name = f'{inpath.name}.zip'
        outfile = inpath.parent.joinpath(name)

    # Check if the output is valid
    # TODO: This is a crude check that can still end up creating invalid names.
    if not outfile.name.endswith('.zip'):
        outfile.name = f'{outfile.name}.zip'
    logger.debug("Output file: %s", outfile)
    
    # Write all of the contents of the input to the zip archive
    try:
        with zipfile.ZipFile(outfile, 'w') as archive:
            for item in inpath.rglob('*'):
                archive.write(item, arcname=item.name)
    except (zipfile.BadZipFile, zipfile.LargeZipFile) as err:
        logger.exception("Unable to create zip archive.")
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

    # Get a list of layers within the GPKG file
    existing_layers = fiona.listlayers(gpkg_path)
    logger.debug("GPKG contains layers: %s", existing_layers)

    # Look for matches, and store the layer as a DataFrame. Layer names in geopackages have names that include their
    # version information. The name is always at the end though.
    logger.debug("Loading spatial layers.")
    for layer_name in spatial_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                logger.debug("Reading %s from %s in GPKG", layer_slug, gpkg_layer)
                dframes[layer_name] = gpd.read_file(gpkg_path, layer=gpkg_layer)

    # Create sqlite connection string to load attribute tables directly.
    # This is required because geopandas will throw an error on a dataset that has no geometry.
    conn_str = f'sqlite:///{gpkg_path}'
    logger.debug("Loading attribute layers from %s", conn_str)

    for layer_name in attribute_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                logger.debug("Reading %s from %s in GPKG", layer_slug, gpkg_layer)
                dframes[layer_name] = pd.read_sql_table(gpkg_layer, con=conn_str, coerce_float=False)
    
    # Generate a warning for every table that could not be found.
    for layer in (spatial_layers + attribute_layers):
        if layer not in dframes:
            logger.warning("Layer not found: %s", layer)
    
    # Return everything that was found.
    return dframes

def get_gpkg_filename(identifier: str, major: int, minor: int, lang: str='en') -> str:
    """Generate a name for a GPKG file that is conformant to NRN specifications."""
    nrn_id = 'NRN'
    if lang == 'fr':
        nrn_id = 'RRN'

    # If the identifier is not valid string an exception would be thrown.
    if type(identifier) is not str:
        identifier = str(identifier)

    fname = f'{nrn_id}_{identifier.upper()}_{major}_{minor}_GPKG_{lang}.gpkg'
    return fname

def get_shp_filename(identifier: str, major: int, minor: int, lang: str='en') -> str:
    """Generate a name for a Shapefile file that is conformant to NRN specifications."""
    nrn_id = 'NRN'
    if lang == 'fr':
        nrn_id = 'RRN'

    # If the slug or identifier are not valid strings an exception would be thrown.
    if type(slug) is not str:
        slug = str(slug)
    if type(identifier) is not str:
        identifier = str(identifier)

    fname = f'{nrn_id}_{identifier.upper()}_{major}_{minor}_SHP_{lang}.shp'
    return fname

def get_gml_filename(slug: str, identifier: str, major: int, minor: int, lang: str='en') -> str:
    """Generate a name for a GML file that is conformant to NRN specifications."""
    nrn_id = 'NRN'
    if lang == 'fr':
        nrn_id = 'RRN'

    # If the slug or identifier are not valid strings an exception would be thrown.
    if type(slug) is not str:
        slug = str(slug)
    if type(identifier) is not str:
        identifier = str(identifier)
    
    # Only 'GEOM' and 'ADDR' are considered valid slug values.
    if slug not in ('GEOM', 'ADDR'):
        raise ValueError("Invalid NRN GML file type")

    fname = f'{nrn_id}_{identifier.upper()}_{major}_{minor}_{slug.upper()}.shp'
    return fname

def get_kml_filename(identifier: str, lang: str='en') -> str:
    """Generate a name for a KML file that is conformant to NRN specifications."""
    nrn_id = 'nrn_rrn'

    if type(identifier) is not str:
        identifier = str(identifier)

    fname = f'{nrn_id}_{identifier.lower()}_kml_{lang}.shp'
    return fname

# Table definitions that can exist in each dataset.
class BaseTable:
    """Superclass to layers within a dataset."""
    def __init__(self, key: str, name_en: str, name_fr: str):
        logger.debug("BaseTable initialization started")

        logger.debug("Table %s with names: en=%s, fr=%s", key, name_en, name_fr)
        self.key = key
        self._name_en = name_en
        self._name_fr = name_fr

        # Common fields
        self.fields = ['nid', 'credate', 'revdate', 'datasetnam', 'acqtech', 'specvers']
        logger.debug("Fields decalred: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

        logger.debug("BaseTable initialization complete")
    
    def __repr__(self):
        """Print the class key and shape type when printing to user readable output."""
        return f'{self.key} <{ogr.GeometryTypeToName(self.shape_type)}>'

    def get_gpkg_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name for the layer in GPKG outputs."""
        if lang == 'en':
            slug = self._name_en
            nrn_id = 'NRN'
        else:
            slug = self._name_fr
            nrn_id = 'RRN'

        # Ensure source is a string to avoid any exceptions.
        if type(source) is not str:
            source = str(source)
        
        name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug.upper()}'
        return name
    
    def get_shp_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name to be used for each of the files in a shapefile."""
        if lang == 'en':
            slug = self._name_en
            nrn_id = 'NRN'
        else:
            slug = self._name_fr
            nrn_id = 'RRN'

        # Ensure source is a string to avoid any exceptions.
        if type(source) is not str:
            source = str(source)
        
        name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug.upper()}'
        return name
    
    def get_gml_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name to be used in GML files.
        
        This is an abstract implementation that is meant to be overridden.
        """
        warnings.warn("get_gml_name is meant to be overridden", ResourceWarning)
        return ''

    def get_kml_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name to be used in KML files.
        
        This is an abstract implementation that is meant to be overridden.
        """
        warnings.warn("get_kml_name is meant to be overridden", ResourceWarning)
        return ''

class AddressRangeTable(BaseTable):
    """Definition of the address range table."""

    def __init__(self):
        logger.debug("%s initialization started", self.__class__.__name__)
        super().__init__('addrange', 'ADDRANGE', 'INTERVADR')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'l_altnamnid', 'r_altnamnid', 'l_digdirfg', 
                            'r_digdirfg', 'l_hnumf', 'r_hnumf', 'l_hnumsuff', 'r_hnumsuff', 'l_hnumtypf',
                            'r_hnumtypf', 'l_hnumstr', 'r_hnumstr', 'l_hnuml', 'r_hnuml', 'l_hnumsufl',
                            'r_hnumsufl', 'l_hnumtypl', 'r_hnumtypl', 'l_offnanid', 'r_offnanid', 'l_rfsysind',
                            'r_rfsysind'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class AlternateNameLinkTable(BaseTable):
    """Definition of the Alternate Name Link table."""
    def __init__(self):
        super().__init__('altnamlink', 'ALTNAMELINK', 'LIENNOFF')

        self.fields.extend(['strnamenid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class BlockedPassageTable(BaseTable):
    """Definition of the Blocked Passage table."""
    def __init__(self):
        super().__init__('blkpassage', 'BLKPASSAGE', 'PASSAGEOBS')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'blkpassty', 'roadnid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class FerrySegmentTable(BaseTable):
    """Definition of the Ferry Segment table."""
    def __init__(self):
        super().__init__('ferryseg', 'FERRYSEG', 'SLIAISONTR')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'closing', 'ferrysegid', 'roadclass',
                            'rtename1en', 'rtename2en', 'rtename3en', 'rtename4en',
                            'rtename1fr', 'rtename2fr', 'rtename3fr', 'rtename4fr',
                            'rtnumber1', 'rtnumber2', 'rtnumber3', 'rtnumber4', 'rtnumber5'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbLineString
        logger.debug("Shape type: %s", self.shape_type)

class JunctionTable(BaseTable):
    """Definition of the Junction table."""
    def __init__(self):
        super().__init__('junction', 'JUNCTION', 'JONCTION')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'exitnbr', 'junctype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class RoadSegmentTable(BaseTable):
    """Definition of the road segment table."""
    def __init__(self):
        super().__init__('roadseg', 'ROADSEG', 'SEGMROUT')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'l_adddirfg', 'r_adddirfg', 'adrangenid',
                            'closing', 'exitnbr', 'l_hnumf', 'r_hnumf', 'roadclass', 'l_hnuml', 'r_hnuml',
                            'nbrlanes', 'l_placenam', 'r_placenam', 'l_stname_c', 'r_stname_c', 'pavsurf',
                            'pavstatus', 'roadjuris', 'roadsegid',
                            'rtename1en', 'rtename2en', 'rtename3en', 'rtename4en',
                            'rtename1fr', 'rtename2fr', 'rtename3fr', 'rtename4fr',
                            'rtnumber1', 'rtnumber2', 'rtnumber3', 'rtnumber4', 'rtnumber5',
                            'speed', 'strunameen', 'strunamefr', 'structid', 'structtype', 'trafficdir', 'unpavsurf'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbLineString
        logger.debug("Shape type: %s", self.shape_type)

class StreetPlaceNameTable(BaseTable):
    """Definition of the street and place name table."""
    def __init__(self):
        super().__init__('strplaname', 'STRPLANAME', 'NOMRUELIEU')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'dirprefix', 'dirsuffix', 'muniquad', 'placename',
                            'placetype', 'province', 'starticle', 'namebody', 'strtypre', 'strtysuf'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class TollPointTable(BaseTable):
    """Definition of the toll point table."""
    def __init__(self):
        super().__init__('tollpoint', 'TOLLPOINT', 'POSTEPEAGE')

        self.fields.extend(['metacover', 'accuracy', 'provider', 'roadnid', 'tollpttype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)
