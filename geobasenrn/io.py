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
import warnings
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

def get_gpkg_filename(identifier: str, major: int, minor: int, lang: str='en') -> str:
    """Generate a name for a GPKG file that is conformant to NRN specifications."""
    nrn_id = 'NRN'
    if lang == 'fr':
        nrn_id = 'RRN'

    # If the slug or identifier are not valid strings an exception would be thrown.
    if type(slug) is not str:
        slug = str(slug)
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
    def __init__(self, name_en, name_fr):
        self.name_en = name_en
        self.name_fr = name_fr

        # Common fields
        self.fields = {
            'nid': ogr.FieldDefn("NID", ogr.OFTString),
            'credate': ogr.FieldDefn('CREDATE', ogr.OFTString),
            'revdate': ogr.FieldDefn('REVDATE', ogr.OFTString),
            'datasetnam': ogr.FieldDefn('DATASETNAM', ogr.OFTString),
            'acqtech': ogr.FieldDefn('ACQTECH', ogr.OFTString),
            'specvers': ogr.FieldDefn('SPECVERS', ogr.OFTReal),
        }

        self.shape_type = ogr.wkbNone
    
    def _set_field_width(self, field_name: str, width: int):
        """Set the field width for the given field."""

        if field_name not in self.fields:
            raise ValueError("Cannot set width on undeclared field.")

        self.fields[field_name].setWidth(width)

    def _set_field_widths(self):
        """Set the width of each field in self.fields."""

        widths = {
            'nid': 32,
            'credate': 8,
            'revdate': 8,
            'datasetnam': 25,
            'acqtech': 23,
            'specvers': 10,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

    def get_gpkg_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name for the layer in GPKG outputs."""
        if lang == 'en':
            slug = self.name_en
            nrn_id = 'NRN'
        else:
            slug = self.name_fr
            nrn_id = 'RRN'

        # Ensure source is a string to avoid any exceptions.
        if type(source) is not str:
            source = str(source)
        
        name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug.upper()}'
        return name
    
    def get_shp_layer_name(self, source, major, minor, lang='en'):
        """Generate a valid name to be used for each of the files in a shapefile."""
        if lang == 'en':
            slug = self.name_en
            nrn_id = 'NRN'
        else:
            slug = self.name_fr
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
        super().__init__('addrange', 'INTERVADR')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'l_altnamnid': ogr.FieldDefn('L_ALTNANID', ogr.OFTString),
            'r_altnamnid': ogr.FieldDefn('R_ALTNANID', ogr.OFTString),
            'l_digdirfg': ogr.FieldDefn('L_DIGDIRFG', ogr.OFTString),
            'r_digdirfg': ogr.FieldDefn('R_DIGDIRFG', ogr.OFTString),
            'l_hnumf': ogr.FieldDefn('L_HNUMF', ogr.OFTString),
            'r_hnumf': ogr.FieldDefn('R_HNUMF', ogr.OFTString),
            'l_hnumsuff': ogr.FieldDefn('L_HNUMSUFF', ogr.OFTString),
            'r_hnumsuff': ogr.FieldDefn('R_HNUMSUFF', ogr.OFTString),
            'l_hnumtypf': ogr.FieldDefn('L_HNUMTYPF', ogr.OFTString),
            'r_hnumtypf': ogr.FieldDefn('R_HNUMTYPF', ogr.OFTString),
            'l_hnumstr': ogr.FieldDefn('L_HNUMSTR', ogr.OFTString),
            'r_hnumstr': ogr.FieldDefn('R_HNUMSTR', ogr.OFTString),
            'l_hnuml': ogr.FieldDefn('L_HNUML', ogr.OFTString),
            'r_hnuml': ogr.FieldDefn('R_HNUML', ogr.OFTString),
            'l_hnumsufl': ogr.FieldDefn('L_HNUMSUFL', ogr.OFTString),
            'r_hnumsufl': ogr.FieldDefn('R_HNUMSUFL', ogr.OFTString),
            'l_hnumtypl': ogr.FieldDefn('L_HNUMTYPL', ogr.OFTString),
            'r_hnumtypl': ogr.FieldDefn('R_HNUMTYPL', ogr.OFTString),
            'l_offnanid': ogr.FieldDefn('L_OFFNANID', ogr.OFTString),
            'r_offnanid': ogr.FieldDefn('R_OFFNANID', ogr.OFTString),
            'l_rfsysind': ogr.FieldDefn('L_RFSYSIND', ogr.OFTString),
            'r_rfsysind': ogr.FieldDefn('R_RFSYSIND', ogr.OFTString)
        })

        self.shape_type = ogr.wkbNone
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider': 24,
            'l_altnamnid': 32,
            'r_altnamnid': 32,
            'l_digdirfg': 18,
            'r_digdirfg': 18,
            'l_hnumf': 9,
            'r_hnumf': 9,
            'l_hnumsuff': 10,
            'r_hnumsuff': 10,
            'l_hnumtypf': 16,
            'r_hnumtypf': 16,
            'l_hnumstr': 9,
            'r_hnumstr': 9,
            'l_hnuml': 9,
            'r_hnuml': 9,
            'l_hnumsufl': 10,
            'r_hnumsufl': 10,
            'l_hnumtypl': 16,
            'r_hnumtypl': 16,
            'l_offnanid': 32,
            'r_offnanid': 32,
            'l_rfsysind': 18,
            'r_rfsysind': 18
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class AlternateNameLinkTable(BaseTable):
    """Definition of the Alternate Name Link table."""
    def __init__(self):
        super().__init__('altnamlink', 'LIENNOFF')

        self.fields.update({
            'strnamenid': ogr.FieldDefn('STRNAMENID', ogr.OFTString)
        })

        self.shape_type = ogr.wkbNone

    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        self._set_field_width('strnamenid', 32)

class BlockedPassageTable(BaseTable):
    """Definition of the Blocked Passage table."""
    def __init__(self):
        super().__init__('blkpassage', 'PASSAGEOBS')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'blkpassty': ogr.FieldDefn('BLKPASSTY', ogr.OFTString),
            'roadnid': ogr.FieldDefn('ROADNID', ogr.OFTString)
        })

        self.shape_type = ogr.wkbPoint
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'blkpassty': 17,
            'roadnid': 32,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class FerrySegmentTable(BaseTable):
    """Definition of the Ferry Segment table."""
    def __init__(self):
        super().__init__('ferryseg', 'SLIAISONTR')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'closing': ogr.FieldDefn('CLOSING', ogr.OFTString),
            'ferrysegid': ogr.FieldDef('FERRYSEGID', ogr.OFTInteger),
            'roadclass': ogr.FieldDefn('ROADCLASS', ogr.OFTString),
            'rtename1en': ogr.FieldDefn('RTENAME1EN', ogr.OFTString),
            'rtename2en': ogr.FieldDefn('RTENAME2EN', ogr.OFTString),
            'rtename3en': ogr.FieldDefn('RTENAME3EN', ogr.OFTString),
            'rtename4en': ogr.FieldDefn('RTENAME4EN', ogr.OFTString),
            'rtename1fr': ogr.FieldDefn('RTENAME1FR', ogr.OFTString),
            'rtename2fr': ogr.FieldDefn('RTENAME2FR', ogr.OFTString),
            'rtename3fr': ogr.FieldDefn('RTENAME3FR', ogr.OFTString),
            'rtename4fr': ogr.FieldDefn('RTENAME4FR', ogr.OFTString),
            'rtnumber1': ogr.FieldDefn('RTNUMBER1', ogr.OFTString),
            'rtnumber2': ogr.FieldDefn('RTNUMBER2', ogr.OFTString),
            'rtnumber3': ogr.FieldDefn('RTNUMBER3', ogr.OFTString),
            'rtnumber4': ogr.FieldDefn('RTNUMBER4', ogr.OFTString),
            'rtnumber5': ogr.FieldDefn('RTNUMBER5', ogr.OFTString),
        })

        self.shape_type = ogr.wkbLineString
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'closing': 7,
            'ferrysegid': 9,
            'roadclass': 21,
            'rtename1en': 100,
            'rtename2en': 100,
            'rtename3en': 100,
            'rtename4en': 100,
            'rtename1fr': 100,
            'rtename2fr': 100,
            'rtename3fr': 100,
            'rtename4fr': 100,
            'rtnumber1': 10,
            'rtnumber2': 10,
            'rtnumber3': 10,
            'rtnumber4': 10,
            'rtnumber5': 10,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class JunctionTable(BaseTable):
    """Definition of the Junction table."""
    def __init__(self):
        super().__init__('junction', 'JONCTION')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'exitnbr': ogr.FieldDefn('EXITNBR', ogr.OFTString),
            'junctype': ogr.FieldDefn('JUNCTYPE', ogr.OFTString),
        })

        self.shape_type = ogr.wkbPoint
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'exitnbr': 10,
            'junctype': 12,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class RoadSegmentTable(BaseTable):
    """Definition of the road segment table."""
    def __init__(self):
        super().__init__('roadseg', 'SEGMROUT')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'l_adddirfg': ogr.FieldDefn('L_ADDDIRFG', ogr.OFTString),
            'r_adddirfg': ogr.FieldDefn('R_ADDDIRFG', ogr.OFTString),
            'adrangenid': ogr.FieldDefn('ADRANGENID', ogr.OFTString),
            'closing': ogr.FieldDefn('CLOSING', ogr.OFTString),
            'exitnbr': ogr.FieldDefn('EXITNBR', ogr.OFTString),
            'l_hnumf': ogr.FieldDefn('L_HNUMF', ogr.OFTString),
            'r_hnumf': ogr.FieldDefn('R_HNUMF', ogr.OFTString),
            'roadclass': ogr.FieldDefn('ROADCLASS', ogr.OFTString),
            'l_hnuml': ogr.FieldDefn('L_HNUML', ogr.OFTString),
            'r_hnuml': ogr.FieldDefn('R_HNUML', ogr.OFTString),
            'nbrlanes': ogr.FieldDefn('NBRLANES', ogr.OFTInteger),
            'l_placenam': ogr.FieldDefn('L_PLACENAM', ogr.OFTString),
            'r_placenam': ogr.FieldDefn('R_PLACENAM', ogr.OFTString),
            'l_stname_c': ogr.FieldDefn('L_STNAME_C', ogr.OFTString),
            'r_stname_c': ogr.FieldDefn('R_STNAME_C', ogr.OFTString),
            'pavsurf': ogr.FieldDefn('PAVSURF', ogr.OFTString),
            'pavstatus': ogr.FieldDefn('PAVSTATUS', ogr.OFTString),
            'roadjuris': ogr.FieldDefn('ROADJURIS', ogr.OFTString),
            'roadsegid': ogr.FieldDefn('ROADSEGID', ogr.OFTInteger),
            'rtename1en': ogr.FieldDefn('RTENAME1EN', ogr.OFTString),
            'rtename2en': ogr.FieldDefn('RTENAME2EN', ogr.OFTString),
            'rtename3en': ogr.FieldDefn('RTENAME3EN', ogr.OFTString),
            'rtename4en': ogr.FieldDefn('RTENAME4EN', ogr.OFTString),
            'rtename1fr': ogr.FieldDefn('RTENAME1FR', ogr.OFTString),
            'rtename2fr': ogr.FieldDefn('RTENAME2FR', ogr.OFTString),
            'rtename3fr': ogr.FieldDefn('RTENAME3FR', ogr.OFTString),
            'rtename4fr': ogr.FieldDefn('RTENAME4FR', ogr.OFTString),
            'rtnumber1': ogr.FieldDefn('RTNUMBER1', ogr.OFTString),
            'rtnumber2': ogr.FieldDefn('RTNUMBER2', ogr.OFTString),
            'rtnumber3': ogr.FieldDefn('RTNUMBER3', ogr.OFTString),
            'rtnumber4': ogr.FieldDefn('RTNUMBER4', ogr.OFTString),
            'rtnumber5': ogr.FieldDefn('RTNUMBER5', ogr.OFTString),
            'speed': ogr.FieldDefn('SPEED', ogr.OFTInteger),
            'strunameen': ogr.FieldDefn('STRUNAMEEN', ogr.OFTString),
            'strunamefr': ogr.FieldDefn('STRUNAMEFR', ogr.OFTString),
            'structid': ogr.FieldDefn('STRUCTID', ogr.OFTString),
            'structtype': ogr.FieldDefn('STRUCTTYPE', ogr.OFTString),
            'trafficdir': ogr.FieldDefn('TRAFFICDIR', ogr.OFTString),
            'unpavsurf': ogr.FieldDefn('UNPAVSURF', ogr.OFTString),
        })

        self.shape_type = ogr.wkbLineString
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'l_adddirfg': 18,
            'r_adddirfg': 18,
            'adrangenid': 32,
            'closing': 7,
            'exitnbr': 10,
            'l_hnumf': 30,
            'r_hnumf': 30,
            'roadclass': 21,
            'l_hnuml': 30,
            'r_hnuml': 30,
            'nbrlanes': 4,
            'l_placenam': 100,
            'r_placenam': 100,
            'l_stname_c': 100,
            'r_stname_c': 100,
            'rtename1en': 100,
            'rtename2en': 100,
            'rtename3en': 100,
            'rtename4en': 100,
            'rtename1fr': 100,
            'rtename2fr': 100,
            'rtename3fr': 100,
            'rtename4fr': 100,
            'rtnumber1': 10,
            'rtnumber2': 10,
            'rtnumber3': 10,
            'rtnumber4': 10,
            'rtnumber5': 10,
            'speed': 4,
            'strunameen': 100),
            'strunamefr': 100,
            'structid': 32,
            'structtype': 15,
            'trafficdir': 18,
            'unpavsurf': 7,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class StreetPlaceNameTable(BaseTable):
    """Definition of the street and place name table."""
    def __init__(self):
        super().__init__('strplaname', 'NOMRUELIEU')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'dirprefix': ogr.FieldDefn('DIRPREFIX', ogr.OFTString),
            'dirsuffix': ogr.FieldDefn('DIRSUFFIX', ogr.OFTString),
            'muniquad': ogr.FieldDefn('MUNIQUAD', ogr.OFTString),
            'placename': ogr.FieldDefn('PLACENAME', ogr.OFTString),
            'placetype': ogr.FieldDefn('PLACETYPE', ogr.OFTString),
            'province': ogr.FieldDefn('PROVINCE', ogr.OFTString),
            'starticle': ogr.FieldDefn('STARTICLE', ogr.OFTString),
            'namebody': ogr.FieldDefn('NAMEBODY', ogr.OFTString),
            'strtypre': ogr.FieldDefn('STRTYPRE', ogr.OFTString),
            'strtysuf': ogr.FieldDefn('STRTYSUF', ogr.OFTString),
        })

        self.shape_type = ogr.wkbNone
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'dirprefix': 10,
            'dirsuffix': 10,
            'muniquad': 10,
            'placename': 100,
            'placetype': 100
            'starticle': 20,
            'namebody': 50,
            'strtypre': 30,
            'strtysuf': 30
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])

class TollPointTable(BaseTable):
    """Definition of the toll point table."""
    def __init__(self):
        super().__init__('tollpoint', 'POSTEPEAGE')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'roadnid': ogr.FieldDefn('ROADNID', ogr.OFTString),
            'tollpttype': ogr.FieldDefn('TOLLPTTYPE', ogr.OFTString)
        })

        self.shape_type = ogr.wkbPoint
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        widths = {
            'metacover': 8,
            'accuracy': 4,
            'provider':24,
            'roadnid': 32,
            'tollpttype': 22,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])
