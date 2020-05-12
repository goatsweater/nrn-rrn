"""Definitions for valid layers within an NRN dataset."""

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

def df_to_gpkg(gpkg: Path, df: pd.DataFrame, table_name: str):
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
    logger.debug("GPKG contains layers: %s", existing_layers)

    # Look for matches, and store the layer as a DataFrame. Layer names in geopackages have names that include their
    # version information. The name is always at the end though.
    for layer_name in spatial_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                logger.debug("Reading %s from GPKG", gpkg_layer)
                dframes[layer_name] = gpd.read_file(gpkg_path, layer=gpkg_layer)

    # Create sqlite connection string to load attribute tables directly.
    conn_str = f'sqlite:///{gpkg_path}'
    logger.debug("Loading attribute layers from %s", conn_str)

    for layer_name in attribute_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                logger.debug("Reading %s from GPKG", gpkg_layer)
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
    def __init__(self, name_en, name_fr):
        logger.debug("BaseTable initialization started")

        logger.debug("Table names: en=%s, fr=%s", name_en, name_fr)
        self._name_en = name_en
        self._name_fr = name_fr

        # Common fields
        self.fields = {
            'nid': ogr.FieldDefn('NID', ogr.OFTString),
            'credate': ogr.FieldDefn('CREDATE', ogr.OFTString),
            'revdate': ogr.FieldDefn('REVDATE', ogr.OFTString),
            'datasetnam': ogr.FieldDefn('DATASETNAM', ogr.OFTString),
            'acqtech': ogr.FieldDefn('ACQTECH', ogr.OFTString),
            'specvers': ogr.FieldDefn('SPECVERS', ogr.OFTReal),
        }
        logger.debug("Fields decalred: %s", self.fields.keys())

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

        logger.debug("BaseTable initialization complete")
    
    def _set_field_width(self, field_name: str, width: int):
        """Set the field width for the given field."""
        logger.debug("Setting field width for %s to %s", field_name, width)

        if field_name not in self.fields:
            raise ValueError("Cannot set width on undeclared field.")

        self.fields[field_name].SetWidth(width)
    
    def _set_field_name(self, field: str, name: str):
        """Set the name of a field."""
        if name == None or name == '':
            raise ValueError("Invalid field name.")

        logger.debug("Setting field name on %s to %s", field, name)
        self.fields[field].SetName(name)

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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        # only languages supported are en and fr
        if lang.lower() not in ('en', 'fr'):
            raise ValueError(f'Unsupported language code: {lang}')

        # Define the name of each field for each language
        field_names = {
            'en': {
                'nid': 'NID',
                'credate': 'CREDATE',
                'revdate': 'REVDATE',
                'datasetnam': 'DATASETNAM',
                'acqtech': 'ACQTECH',
                'specvers': 'SPECVERS',
            },
            'fr': {
                'nid': 'IDN',
                'credate': 'DATECRE',
                'revdate': 'DATEREV',
                'datasetnam': 'NOMJEUDONN',
                'acqtech': 'TECHACQ',
                'specvers': 'VERSNORMES',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

class AddressRangeTable(BaseTable):
    """Definition of the address range table."""

    def __init__(self):
        logger.debug("%s initialization started", self.__class__.__name__)
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
        logger.debug("Fields: %s", self.fields.keys())

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

        # Set the width of all the fields.
        self._set_field_widths()
    
    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'l_altnamnid': 'L_ALTNANID',
                'r_altnamnid': 'R_ALTNANID',
                'l_digdirfg': 'L_DIGDIRFG',
                'r_digdirfg': 'R_DIGDIRFG',
                'l_hnumf': 'L_HNUMF',
                'r_hnumf': 'R_HNUMF',
                'l_hnumsuff': 'L_HNUMSUFF',
                'r_hnumsuff': 'R_HNUMSUFF',
                'l_hnumtypf': 'L_HNUMTYPF',
                'r_hnumtypf': 'R_HNUMTYPF',
                'l_hnumstr': 'L_HNUMSTR',
                'r_hnumstr': 'R_HNUMSTR',
                'l_hnuml': 'L_HNUML',
                'r_hnuml': 'R_HNUML',
                'l_hnumsufl': 'L_HNUMSUFL',
                'r_hnumsufl': 'R_HNUMSUFL',
                'l_hnumtypl': 'L_HNUMTYPL',
                'r_hnumtypl': 'R_HNUMTYPL',
                'l_offnanid': 'L_OFFNANID',
                'r_offnanid': 'R_OFFNANID',
                'l_rfsysind': 'L_RFSYSIND',
                'r_rfsysind': 'R_RFSYSIND'
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'l_altnamnid': 'IDNOMNOF_G',
                'r_altnamnid': 'IDNOMNOF_D',
                'l_digdirfg': 'SENSNUM_G',
                'r_digdirfg': 'SENSNUM_D',
                'l_hnumf': 'NUMP_G',
                'r_hnumf': 'NUMP_D',
                'l_hnumsuff': 'SUFNUMP_G',
                'r_hnumsuff': 'SUFNUMP_D',
                'l_hnumtypf': 'TYPENUMP_G',
                'r_hnumtypf': 'TYPENUMP_D',
                'l_hnumstr': 'STRUNUM_G',
                'r_hnumstr': 'STRUNUM_D',
                'l_hnuml': 'NUMD_G',
                'r_hnuml': 'NUMD_D',
                'l_hnumsufl': 'SUFNUMD_G',
                'r_hnumsufl': 'SUFNUMD_D',
                'l_hnumtypl': 'TYPENUMD_G',
                'r_hnumtypl': 'TYPENUMD_D',
                'l_offnanid': 'IDNOMOFF_G',
                'r_offnanid': 'IDNOMOFF_D',
                'l_rfsysind': 'SYSREF_G',
                'r_rfsysind': 'SYSREF_D'
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

class AlternateNameLinkTable(BaseTable):
    """Definition of the Alternate Name Link table."""
    def __init__(self):
        super().__init__('altnamlink', 'LIENNOFF')

        self.fields.update({
            'strnamenid': ogr.FieldDefn('STRNAMENID', ogr.OFTString)
        })

        self.shape_type = ogr.wkbNone

        # Set the width of all the fields.
        self._set_field_widths()

    def _set_field_widths(self):
        """Set the width of each field in self.fields."""
        super()._set_field_widths()

        self._set_field_width('strnamenid', 32)
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'strnamenid': '',
            },
            'fr': {
                'strnamenid': 'IDNOMRUE',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'blkpassty': 'BLKPASSTY',
                'roadnid': 'ROADNID',
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'blkpassty': 'TYPEOBSTRU',
                'roadnid': 'IDNELEMRTE',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

class FerrySegmentTable(BaseTable):
    """Definition of the Ferry Segment table."""
    def __init__(self):
        super().__init__('ferryseg', 'SLIAISONTR')

        self.fields.update({
            'metacover': ogr.FieldDefn('METACOVER', ogr.OFTString),
            'accuracy': ogr.FieldDefn('ACCURACY', ogr.OFTInteger),
            'provider': ogr.FieldDefn('PROVIDER', ogr.OFTString),
            'closing': ogr.FieldDefn('CLOSING', ogr.OFTString),
            'ferrysegid': ogr.FieldDefn('FERRYSEGID', ogr.OFTInteger),
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

        # Set the width of all the fields.
        self._set_field_widths()
    
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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'closing': 'CLOSING',
                'ferrysegid': 'FERRYSEGID',
                'roadclass': 'ROADCLASS',
                'rtename1en': 'RTENAME1EN',
                'rtename2en': 'RTENAME2EN',
                'rtename3en': 'RTENAME3EN',
                'rtename4en': 'RTENAME4EN',
                'rtename1fr': 'RTENAME1FR',
                'rtename2fr': 'RTENAME2FR',
                'rtename3fr': 'RTENAME3FR',
                'rtename4fr': 'RTENAME4FR',
                'rtnumber1': 'RTNUMBER1',
                'rtnumber2': 'RTNUMBER2',
                'rtnumber3': 'RTNUMBER3',
                'rtnumber4': 'RTNUMBER4',
                'rtnumber5': 'RTNUMBER5',
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'closing': 'FERMETURE',
                'ferrysegid': 'IDSEGMLTR',
                'roadclass': 'CLASSROUTE',
                'rtename1en': 'NOMRTE1AN',
                'rtename2en': 'NOMRTE2AN',
                'rtename3en': 'NOMRTE3AN',
                'rtename4en': 'NOMRTE4AN',
                'rtename1fr': 'NOMRTE1FR',
                'rtename2fr': 'NOMRTE2FR',
                'rtename3fr': 'NOMRTE3FR',
                'rtename4fr': 'NOMRTE4FR',
                'rtnumber1': 'NUMROUTE1',
                'rtnumber2': 'NUMROUTE2',
                'rtnumber3': 'NUMROUTE3',
                'rtnumber4': 'NUMROUTE4',
                'rtnumber5': 'NUMROUTE5',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

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

        # Set the width of all the fields.
        self._set_field_widths()
    
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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'exitnbr': 'EXITNBR',
                'junctype': 'JUNCTYPE',
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'exitnbr': 'NUMSORTIE',
                'junctype': 'TYPEJONC',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

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

        # Set the width of all the fields.
        self._set_field_widths()
    
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
            'pavsurf': 8,
            'pavstatus': 7,
            'roadjuris': 100,
            'roadsegid': 9,
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
            'strunameen': 100,
            'strunamefr': 100,
            'structid': 32,
            'structtype': 15,
            'trafficdir': 18,
            'unpavsurf': 7,
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'l_adddirfg': 'L_ADDDIRFG',
                'r_adddirfg': 'R_ADDDIRFG',
                'adrangenid': 'ADRANGENID',
                'closing': 'CLOSING',
                'exitnbr': 'EXITNBR',
                'l_hnumf': 'L_HNUMF',
                'r_hnumf': 'R_HNUMF',
                'roadclass': 'ROADCLASS',
                'l_hnuml': 'L_HNUML',
                'r_hnuml': 'R_HNUML',
                'nbrlanes': 'NBRLANES',
                'l_placenam': 'L_PLACENAM',
                'r_placenam': 'R_PLACENAM',
                'l_stname_c': 'L_STNAME_C',
                'r_stname_c': 'R_STNAME_C',
                'pavsurf': 'PAVSURF',
                'pavstatus': 'PAVSTATUS',
                'roadjuris': 'ROADJURIS',
                'roadsegid': 'ROADSEGID',
                'rtename1en': 'RTENAME1EN',
                'rtename2en': 'RTENAME2EN',
                'rtename3en': 'RTENAME3EN',
                'rtename4en': 'RTENAME4EN',
                'rtename1fr': 'RTENAME1FR',
                'rtename2fr': 'RTENAME2FR',
                'rtename3fr': 'RTENAME3FR',
                'rtename4fr': 'RTENAME4FR',
                'rtnumber1': 'RTNUMBER1',
                'rtnumber2': 'RTNUMBER2',
                'rtnumber3': 'RTNUMBER3',
                'rtnumber4': 'RTNUMBER4',
                'rtnumber5': 'RTNUMBER5',
                'speed': 'SPEED',
                'strunameen': 'STRUNAMEEN',
                'strunamefr': 'STRUNAMEFR',
                'structid': 'STRUCTID',
                'structtype': 'STRUCTTYPE',
                'trafficdir': 'TRAFFICDIR',
                'unpavsurf': 'UNPAVSURF',
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'l_adddirfg': 'ADRSENS_G',
                'r_adddirfg': 'ADRSENS_D',
                'adrangenid': 'IDINTERVAD',
                'closing': 'FERMETURE',
                'exitnbr': 'NUMSORTIE',
                'l_hnumf': 'NUMP_G',
                'r_hnumf': 'NUMP_D',
                'roadclass': 'CLASSROUTE',
                'l_hnuml': 'NUMD_G',
                'r_hnuml': 'NUMD_D',
                'nbrlanes': 'NBRVOIES',
                'l_placenam': 'NOMLIEU_G',
                'r_placenam': 'NOMLIEU_D',
                'l_stname_c': 'NOMRUE_C_G',
                'r_stname_c': 'NOMRUE_C_D',
                'pavsurf': 'TYPEREV',
                'pavstatus': 'ETATREV',
                'roadjuris': 'AUTORITE',
                'roadsegid': 'IDSEGMRTE',
                'rtename1en': 'NOMRTE1AN',
                'rtename2en': 'NOMRTE2AN',
                'rtename3en': 'NOMRTE3AN',
                'rtename4en': 'NOMRTE4AN',
                'rtename1fr': 'NOMRTE1FR',
                'rtename2fr': 'NOMRTE2FR',
                'rtename3fr': 'NOMRTE3FR',
                'rtename4fr': 'NOMRTE4FR',
                'rtnumber1': 'NUMROUTE1',
                'rtnumber2': 'NUMROUTE2',
                'rtnumber3': 'NUMROUTE3',
                'rtnumber4': 'NUMROUTE4',
                'rtnumber5': 'NUMROUTE5',
                'speed': 'VITESSE',
                'strunameen': 'NOMSTRUCAN',
                'strunamefr': 'NOMSTRUCFR',
                'structid': 'IDSTRUCT',
                'structtype': 'TYPESTRUCT',
                'trafficdir': 'SENSCIRCUL',
                'unpavsurf': 'TYPENONREV',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

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

        # Set the width of all the fields.
        self._set_field_widths()
    
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
            'placetype': 100,
            'starticle': 20,
            'namebody': 50,
            'strtypre': 30,
            'strtysuf': 30
        }

        for fw in widths:
            self._set_field_width(fw, widths[fw])
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'dirprefix': 'DIRPREFIX',
                'dirsuffix': 'DIRSUFFIX',
                'muniquad': 'MUNIQUAD',
                'placename': 'PLACENAME',
                'placetype': 'PLACETYPE',
                'province': 'PROVINCE',
                'starticle': 'STARTICLE',
                'namebody': 'NAMEBODY',
                'strtypre': 'STRTYPRE',
                'strtysuf': 'STRTYSUF'
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'dirprefix': 'PREDIR',
                'dirsuffix': 'SUFDIR',
                'muniquad': 'MUNIQUAD',
                'placename': 'NOMLIEU',
                'placetype': 'TYPELIEU',
                'province': 'PROVINCE',
                'starticle': 'ARTNOMRUE',
                'namebody': 'CORPSNOM',
                'strtypre': 'PRETYPRUE',
                'strtysuf': 'SUFTYPRUE'
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])

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

        # Set the width of all the fields.
        self._set_field_widths()
    
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
    
    def set_gpkg_field_names(self, lang: str='en'):
        """Update the fields to use field names according to the GPKG definition."""
        super().set_gpkg_field_names(lang)

        # Define the name of each field for each language
        field_names = {
            'en': {
                'metacover': 'METACOVER',
                'accuracy': 'ACCURACY',
                'provider': 'PROVIDER',
                'roadnid': 'ROADNID',
                'junctype': 'TOLLPTTYPE',
            },
            'fr': {
                'metacover': 'COUVERMETA',
                'accuracy': 'PRECISION',
                'provider': 'FOURNISSR',
                'roadnid': 'IDNELEMRTE',
                'tollpttype': 'TYPEPTEPEA',
            }
        }

        # Get the name map for the language
        name_map = field_names.get(lang.lower())

        # Set all the field names based on the name map
        for field in name_map:
            self._set_field_name(field, name_map[field])
