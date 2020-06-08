"""Definitions for valid layers within an NRN dataset."""

import fiona
import geobasenrn as nrn
from geobasenrn.schema import schema
import geopandas as gpd
import json
import logging
from osgeo import ogr, osr
import pandas as pd
from pathlib import Path
import requests
import sqlite3
import tempfile
from tqdm import tqdm
import warnings
import zipfile

logger = logging.getLogger(__name__)

# The name of the driver to use when creating output
ogr_drivers = {
    'gpkg': 'GPKG',
    'shp': 'Esri Shapefile',
    'gml': 'GML',
    'kml': 'KML'
}

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

def source_layer_to_dataframe(source_path: Path, source_layer: str = None, source_driver: str = None, source_epsg: int = None, spatial: bool = True):
    """Create a GeoDataFrame from a source dataset for spatial data, or a DataFrame for non-spatial data."""
    # v0.7 of geopandas does not implement support for loading attribute data. It will be in a future release, but 
    # until that happens we need to manually create a DataFrame for attribute tables inside a spatial container.
    logger.debug("Creating DataFrame from file %s, layer %s", source_path, source_layer)
    df = None

    if spatial:
        # Set the CRS of incoming data
        source_crs = source_epsg
        if source_epsg:
            source_crs = f'EPSG:{source_epsg}'
        
        # Load the data into a DataFrame and automatically convert all column names to lower case
        df = (gpd.read_file(source_path, layer_name=source_layer, driver=source_driver, crs=source_crs)
              .rename(columns=str.lower))

        # Reproject the data to match what the NRN expects
        df = df.to_crs(epsg=nrn.SRS_EPSG_CODE)
    else:
        data = []
        with fiona.open(source_path, layer=source_layer, driver=source_driver) as source:
            for feature in source:
                props = feature['properties']
                data.append(props)
        df = pd.DataFrame.from_records(data)
    
    return df

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
    for layer_name in nrn.spatial_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                dframes[layer_name] = source_layer_to_dataframe(gpkg_path, gpkg_layer)

    # Create sqlite connection string to load attribute tables directly.
    # This is required because geopandas will throw an error on a dataset that has no geometry.
    # conn_str = f'sqlite:///{gpkg_path}'
    # logger.debug("Loading attribute layers from %s", conn_str)

    for layer_name in nrn.attribute_layers:
        # Names should be in upper case
        layer_slug = layer_name.upper()
        
        # Check each existing layer
        for gpkg_layer in existing_layers:
            if gpkg_layer.endswith(layer_slug):
                dframes[layer_name] = source_layer_to_dataframe(gpkg_path, gpkg_layer, spatial=False)
                # logger.debug("Reading %s from %s in GPKG", layer_slug, gpkg_layer)
                # dframes[layer_name] = pd.read_sql_table(gpkg_layer, con=conn_str, coerce_float=False)
    
    # Generate a warning for every table that could not be found.
    for layer in (nrn.spatial_layers + nrn.attribute_layers):
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

    # If the identifier is not valid strings an exception would be thrown.
    if type(identifier) is not str:
        identifier = str(identifier)

    fname = f'{nrn_id}_{identifier.upper()}_{major}_{minor}_SHP.shp'
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

    fname = f'{nrn_id}_{identifier.upper()}_{major}_{minor}_{slug}.gml'
    return fname

def get_kml_filename(identifier: str, lang: str='en') -> str:
    """Generate a name for a KML file that is conformant to NRN specifications."""
    nrn_id = 'nrn_rrn'

    if type(identifier) is not str:
        identifier = str(identifier)

    fname = f'{nrn_id}_{identifier.lower()}_kml_{lang}.shp'
    return fname

def get_gpkg_layer_name(layer, source, major, minor, lang='en'):
    """Generate a valid name for the layer in GPKG outputs."""
    if lang == 'en':
        nrn_id = 'NRN'
    else:
        nrn_id = 'RRN'
    
    slug = layer.get_table_name('gpkg', lang)

    # Ensure source is a string to avoid any exceptions.
    if type(source) is not str:
        source = str(source)
    
    name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug.upper()}'
    return name

def get_shp_layer_name(layer, source, major, minor, lang='en'):
    """Generate a valid name to be used for each of the files in a shapefile."""
    if lang == 'en':
        nrn_id = 'NRN'
    else:
        nrn_id = 'RRN'
    
    slug = layer.get_table_name('shp', lang)

    # Ensure source is a string to avoid any exceptions.
    if type(source) is not str:
        source = str(source)
    
    name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug.upper()}'
    return name

def get_gml_layer_name(layer, source, major, minor, lang='en'):
    """Generate a valid name to be used in GML files."""
    if lang == 'en':
        nrn_id = 'NRN'
    else:
        nrn_id = 'RRN'
    
    slug = layer.get_table_name('gml', lang)
    
    # Ensure source is a string to avoid any exceptions.
    if type(source) is not str:
        source = str(source)
    
    name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug}.gml'
    return name

def get_kml_layer_name(layer, source, major, minor, lang='en'):
    """Generate a valid name to be used in KML files.
    """
    warnings.warn("get_kml_name is not implemented yet", ResourceWarning)
    pass

def create_layer(data_source: ogr.DataSource, tbl, layer_name: str, output_format: str, lang: str='en'):
    """Create a layer within the data source that conforms to output format specifications."""
    logger.debug("Creating layer %s for %s in %s", layer_name, tbl.__class__.__name__, output_format)

    if data_source == None:
        raise ValueError('Invalid data source provided')

    # Define the SRS for output data
    logger.debug("Defining spatial reference for output layer")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(nrn.SRS_EPSG_CODE)
    # Don't define a spatial reference on data with no shape.
    if tbl.shape_type == ogr.wkbNone:
        logger.debug("Output layer has no geometry. No spatial reference will be used.")
        srs = None

    # Create the layer
    logger.debug("Creating layer with name %s in %s", layer_name, data_source.GetName())
    layer = data_source.CreateLayer(layer_name, srs, tbl.shape_type)

    # Set the field names to match what is expected for the language
    logger.debug("Creating %s fields", lang)
    for field in tbl.fields:
        field_name = schema[field][output_format][lang]
        field_type = schema[field]['type']
        field_width = schema[field]['width']

        logger.debug("Creating %s field %s", layer_name, field_name)
        # Create a field definiton object.
        field_defn = ogr.FieldDefn(field_name, field_type)
        field_defn.SetWidth(field_width)
        # Create the field on the layer.
        layer.CreateField(field_defn)

def write_data_output(df, layer_name: str, data_source: ogr.DataSource, output_format: str, lang: str='en'):
    """Write the contents of dframes out to output format in the specified work directory.
    
    This creates either a French or English copy of the data, based on the supplied language.
    """
    logger.debug("Writing %s data to %s", layer_name, data_source.GetName())

    # Warn the user if some fields in the DataFrame will not be dumped
    extra_columns = [col for col in df.columns if col not in schema]
    if extra_columns:
        logger.warning("The following columns will not be in the output: %r", extra_columns)
    
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
    # The preferred way to do this would be with a call to geopandas .to_file(), but there is a bug in v0.7 that 
    # prevents appending data to an existing schema.
    # format_driver = ogr_drivers.get(output_format)
    # df.to_file(out_path, layer=layer_name, driver=format_driver, mode="a", index=False)

    # Get the layer within the datasource
    logger.debug("Getting reference to layer %s in output file", layer_name)
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
    logger.debug("Iterating features in the GeoDataFrame and writing to %s.", layer_name)
    # Start a transaction to wrap all the writes. This means non will get written if any fail.
    layer.StartTransaction()
    for feat in tqdm(df.iterfeatures(), total=len(df), desc=f'Writing {layer_name}'):
        # Separate the geometry from the properties to make working with it easier.
        geom_json = json.dumps(feat['geometry'])
        feature_properties = feat['properties']

        # Instantiate a new feature
        feature = ogr.Feature(layer.GetLayerDefn())

        # Iterate all of the properties and add them to the feature.
        for prop in feature_properties:
            # Skip the geometry field - it is intended for use only in setting the geometry
            if prop == 'geometry':
                continue

            # logger.debug("Setting %s=%s", prop, feature_properties[prop])
            field_index = feature.GetFieldIndex(prop)
            if field_index == -1:
                # logger.warning("Field not found in output schema: %s", prop)
                continue

            feature.SetField(field_index, feature_properties[prop])
        
        geom = ogr.CreateGeometryFromJson(geom_json)
        feature.SetGeometry(geom)

        # Save the feature to the layer
        layer.CreateFeature(feature)

        # Clear the pointer before moving on to the next feature
        feature = None
    layer.CommitTransaction()

def write_attr_layer(df, layer: ogr.Layer):
    """Write a DataFrame to a layer."""
    # Iterate each feature in the dataframe and write it to the layer. This will produce a __geo_interface__ compliant
    # dictionary that can be used to get at the records.
    layer_name = layer.GetName()
    logger.debug("Iterating features in the DataFrame and writing to the layer.")
    # Start a transaction to wrap all the writes. This means non will get written if any fail.
    layer.StartTransaction()
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
    layer.CommitTransaction()

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
        """Generate a valid name to be used in GML files."""
        if lang == 'en':
            slug = self._gml_name_en
            nrn_id = 'NRN'
        else:
            slug = self._gml_name_fr
            nrn_id = 'RRN'
        
        # Ensure source is a string to avoid any exceptions.
        if type(source) is not str:
            source = str(source)
        
        name = f'{nrn_id}_{source.upper()}_{major}_{minor}_{slug}.gml'
        return name

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

        # Table names for GML
        self._gml_name_en = 'AddressRange'
        self._gml_name_fr = 'IntervalleAddresse'

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

        # Table names for GML
        self._gml_name_en = 'AlternateNameLink'
        self._gml_name_fr = 'LieuNomNonOfficiel'

        self.fields.extend(['strnamenid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class BlockedPassageTable(BaseTable):
    """Definition of the Blocked Passage table."""
    def __init__(self):
        super().__init__('blkpassage', 'BLKPASSAGE', 'PASSAGEOBS')

        # Table names for GML
        self._gml_name_en = 'BlockedPassage'
        self._gml_name_fr = 'PassageObstrue'

        self.fields.extend(['metacover', 'accuracy', 'provider', 'blkpassty', 'roadnid'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class FerrySegmentTable(BaseTable):
    """Definition of the Ferry Segment table."""
    def __init__(self):
        super().__init__('ferryseg', 'FERRYSEG', 'SLIAISONTR')

        # Table names for GML
        self._gml_name_en = 'FerrySegment'
        self._gml_name_fr = 'SegmentLiaisonTransbordeur'

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

        # Table names for GML
        self._gml_name_en = 'Junction'
        self._gml_name_fr = 'Jonction'

        self.fields.extend(['metacover', 'accuracy', 'provider', 'exitnbr', 'junctype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)

class RoadSegmentTable(BaseTable):
    """Definition of the road segment table."""
    def __init__(self):
        super().__init__('roadseg', 'ROADSEG', 'SEGMROUT')

        # Table names for GML
        self._gml_name_en = 'RoadSegment'
        self._gml_name_fr = 'SegmentRoutier'

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

        # Table names for GML
        self._gml_name_en = 'StreetPlaceName'
        self._gml_name_fr = 'NomRueLieu'

        self.fields.extend(['metacover', 'accuracy', 'provider', 'dirprefix', 'dirsuffix', 'muniquad', 'placename',
                            'placetype', 'province', 'starticle', 'namebody', 'strtypre', 'strtysuf'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbNone
        logger.debug("Shape type: %s", self.shape_type)

class TollPointTable(BaseTable):
    """Definition of the toll point table."""
    def __init__(self):
        super().__init__('tollpoint', 'TOLLPOINT', 'POSTEPEAGE')

        # Table names for GML
        self._gml_name_en = 'TollPoint'
        self._gml_name_fr = 'PostePeage'

        self.fields.extend(['metacover', 'accuracy', 'provider', 'roadnid', 'tollpttype'])
        logger.debug("Fields: %s", self.fields)

        self.shape_type = ogr.wkbPoint
        logger.debug("Shape type: %s", self.shape_type)
