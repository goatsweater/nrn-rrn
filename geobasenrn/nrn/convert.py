"""Convert a provider dataset into valid NRN output.

This conversion does not perform validation against any of the incoming data other than mapping values to their NRN
equivalents when a field has a domain applied to it.
"""

import click
import geobasenrn as nrn
import geobasenrn.io as nrnio
from geobasenrn import schema
from geobasenrn.errors import ConfigurationError
import geopandas as gpd
import logging
import pandas as pd
from pathlib import Path
import tempfile
import yaml


logger = logging.getLogger(__name__)

@click.command()
@click.option('-p', '--previous', 'previous_vintage',
              type=click.Path(dir_okay=False, file_okay=True, resolve_path=True, exists=True),
              help="Path to the previous vintage GPKG file.")
@click.option('-c', '--config', 'config_files',
              type=click.Path(dir_okay=False, file_okay=True, resolve_path=True, exists=True),
              required=True,
              multiple=True,
              help="""Path to the configuration file for this dataset. For datasets with multiple source 
                    configurations, supply multiple arguments.""")
@click.option('-b', '--boundary', 'admin_boundary_path',
              type=click.Path(dir_okay=False, file_okay=True, resolve_path=True, exists=True),
              help="Path to the administrative boundaries file from Statistics Canada.")
@click.pass_context
def convert(ctx, previous_vintage, config_files, admin_boundary_path):
    """Convert an input dataset into an NRN pre-release GPKG."""
    previous_vintage = Path(previous_vintage)
    admin_boundary_path = Path(admin_boundary_path)
    # Stage 1
    # TODO:
    # 1. download previous vintage - done (provided directly)
    # 2. compile source attributes - done
    # 3. compile target attributes
    # 4. compile domains
    # 5. generate source dataframes - done
    # 6. generate target dataframes - done
    # 7. apply field mapping - done
    # 8. recover missing datasets - done
    # 9. apply domains
    # 10. filter strplaname duplicates
    # 11. repair nid linkages
    # 12. save to output

    # Convert all the source configurations into an options dictionary to be referenced throughout conversion.
    config_paths = [Path(f) for f in config_files]
    source_config = get_source_config(config_paths)

    # Load all the source data
    source_data = get_source_data(source_config)

    # Convert all source data to interim format
    dframes = map_source_to_target_dframes(source_config['conform'], source_data)

    # Recover any layers that aren't in the source from the previous vintage
    previous_dframes = nrnio.get_gpkg_contents(previous_vintage)
    for layer in previous_dframes:
        if layer not in dframes:
            dframes[layer] = previous_dframes[layer]

    # Stage 2
    # TODO:
    # 1. load boundaries
    # 2. compile target attributes
    # 3. generate target dataframe
    # 4. generate junctions
    # 5. generate attributes
    # 6. apply domains

    # Load the administrative boundary into a polygon
    admin_boundary = get_admin_boundary_poly(ctx.source_prov, admin_boundary_path)

    # Stage 3
    # TODO:
    # 1. roadseg generate full
    # 2. roadseg generate nids
    # 3. roadseg recover and classify nids
    # 4. roadseg update linkages
    # 5. recover and classify nids
    # 6. export change logs
    # 7. save output

def get_previous_vintage_data(previous_gpkg: Path) -> dict:
    """Convert the previous vintage data into a set dictionary of DataFrames."""
    dframes = nrnio.get_gpkg_contents(previous_gpkg)

    # convert all the columns names in each dataframe to lowercase
    for name, df in dframes.items():
        dframes[name] = df.rename(columns=str.lower)

    return dframes

def get_source_config(config_paths: [Path]) -> dict:
    """Read a source configuration YAML file and build an options dictionary to be used to convert the source data
    into the interim format.

    Each file represents a unique data source, which are merged into a map of where to get data from and how to map
    fields to NRN attributes.
    """
    options = {
        'source_layers': [],
        'conform': {}
    }

    # Load each file one at a time, and add it to the options dictionary
    for path in config_paths:
        try:
            with path.open() as f:
                config_opts = yaml.safe_load(f)
        except (ValueError, yaml.YAMLError):
            logger.exception("Unable to load yaml file: \"{}\".".format(path))
            # This file didn't work, but try loading the next one
            continue

        # The data key defines a source layer
        data_source = config_opts.get('data')
        if data_source == None:
            raise ConfigurationError("Missing 'data' configuration.")

        # Add the data to the set of source layers and record which index it is at
        options['source_layers'].append(data_source)
        source_index = options['source_layers'].index(data_source)

        # Update the field mapping with the information in the conform section
        conformance = config_opts.get('conform')
        if conformance == None:
            raise ConfigurationError("Missing 'conform' configuration.")

        # Each key in conformance is going to be a layer, with a set of fields below it. We want a slightly different
        # structure to be able to map the layer to a source.
        layer_map = {}
        for layer in conformance:
            layer_map[layer] = {
                'source_index': source_index,
                'fields': conformance[layer]
            }
        
        # Record the information in the options
        options['conform'].update(layer_map)
    
    return options

def get_source_layer(layer_name: str, source_path: Path, source_layer: str, source_driver: str = None, 
                     source_epsg: int = None, spatial: bool = True):
    """Load a single layer from a data source.
    
    This builds a single key dictionary where the key is the layer name and the value is the DataFrame. This enables
    the data to be loaded into a collection of source tables for further processing.
    """
    # This is just an attribute table, so no spatial operations to perform. The data could still be in a spatial
    # format container though (GPKG, FGDB). Support is also provided for loading directly from a CSV file.
    if source_path.suffix.lower() == '.csv':
        df = (pd.read_csv(source_path)
              .rename(columns=str.lower))
        return {layer_name: df}
    else:
        df = (nrnio.source_layer_to_dataframe(source_path, source_layer, source_driver, source_epsg, spatial)
              .rename(columns=str.lower))
        return {layer_name: df}

def get_source_data(layer_info: dict) -> dict:
    """Load all source data into a dictionary indexed by the appropriate target layer name."""
    # Keys used to define source data elements in the configuration file
    source_data_path = 'filename'
    source_data_layer = 'layer'
    source_data_driver = 'driver'
    source_data_crs = 'crs'
    source_data_is_spatial = 'spatial'

    # Dictionary for each layer
    dframes = {}

    # Use the layer names in 'conform' as the key for the source data
    conformance = layer_info.get('conform')
    for layer_name in conformance:
        # Gather the data source information
        source_index = conformance[layer_name].get('source_index')
        source_data = layer_info.get('data')[source_index]

        # Get the DataFrame
        source_path = Path(source_data.get(source_data_path))
        source_layer = source_data.get(source_data_layer)
        source_driver = source_data.get(source_data_driver)
        source_crs = source_data.get(source_data_crs)
        is_spatial = source_data.get(source_data_is_spatial, False)

        dframes[layer_name] = get_source_layer(layer_name, source_path, source_layer, source_driver, source_crs)
    
    return dframes

def map_source_to_target_dframes(schema_map: dict, dframes: dict) -> dict:
    """Convert source data into an internal representation convenient for processing."""
    result_dframes = {}

    for item_key in dframes:
        # Figure out which fields are going to be mapped, and how. This breaks down into three basic categories:
        # 1. Fields that map directly - just use the values in the source data
        # 2. Raw text as a value - use a hardcoded string as the value
        # 3. Partial values - apply some function to the data in the column

        field_map = schema_map[item_key]['fields']
        
        direct_map_fields = {}
        raw_values_fields = {}
        function_fields = {}

        for k, v in field_map:
            # Skip any fields that don't have a defined value
            if v == None:
                continue

            # Dictionaries define more complicated processing
            if type(v) is dict:
                function_fields[k] = v
                continue

            # direct map means the value in the schema matches a field in the table definition
            table_fields = schema.class_map[item_key].get_field_names()
            if k in table_fields:
                # this is building a map from old value to new, so invert the key and value here
                direct_map_fields[v] = k
                continue
            
            # This must be a raw value
            raw_values_fields[k] = v
        
        # Direct mapping is just a matter of taking the fields
        source_df = dframes[item_key]
        target_df = source_df[direct_map_fields.values()].rename(columns=direct_map_fields)
        # TODO: remove any extraneous spaces in string data

        # Raw values just get set directly
        for field_name in raw_values_fields:
            target_df[field_name] = raw_values_fields[field_name].strip()
        
        # Apply processing functions
        for target_field, function_set in function_fields:
            target_df = target_df.pipe(apply_functions_to_fields, target_field, function_set)
        
        # Save the target data to be returned
        result_dframes[item_key] = target_df
    
    return result_dframes
        
def apply_functions_to_fields(df, target_field, field_schema):
    """Perform some processing on the values to properly extract the values."""
    new_df = df.copy()

    # define each possible type of function
    def replace(col, pattern, replacement, is_regex: bool = True):
        """Perform text replacement on each item in the column. Set is_regex to False to perform exact matches."""
        return col.str.replace(pattern, replacement, is_regex)

    def extract(col, pattern: str, expand: bool = True):
        """Call re.search and extract a string using a regex pattern."""
        return col.str.extract(pattern, expand)

    def concat(df, join_cols: [str], join_chars: str =''):
        """Combine multiple columns into a single string."""

        # All the columns need to be strings or this will fail.
        # TODO: verify that all columns are strings
        return df[join_cols].agg(join_chars.join, axis=1)

    # Functions that will be applied to entire DataFrames
    df_dispatcher = {
        'concat': concat
    }
    # Functions that will be applied to a Series
    col_dispatcher = {
        'replace': replace,
        'extract': extract
    }

    # Call each defined transformation function in series
    new_df[target_field] = new_df[field_schema['field']]
    for func_call in field_schema['functions']:
        func_name = func_call['function']
        kwargs = func_call.get('args')

        if func_name in df_dispatcher:
            new_df[target_field] = df_dispatcher[func_name](new_df, **kwargs)
        elif func_name in col_dispatcher:
            new_df[target_field] = new_df[target_field].apply(dispatcher[func_name], **kwargs)
    
    return new_df

def get_admin_boundary_poly(source_prov: str, boundary_file_path: Path):
    """Extract the administrative boundary for the given province or territory."""
    # StatCan uses codes instead of ISO identifiers for the area identifiers
    prov_codes = {"ab": 48, "bc": 59, "mb": 46, "nb": 13, "nl": 10, "ns": 12, "nt": 61, "nu": 62, "on": 35, "pe": 11,
                 "qc": 24, "sk": 47, "yt": 60}
    
    # Read the administrative boundaries file and filter it
    query_string = f'pruid == {prov_codes[source_prov.lower()]}'
    boundaries = (gpd.read_file(boundary_file_path)
                  .to_crs(nrn.SRS_EPSG_CODE)
                  .rename(columns=str.lower)
                  .query(query_string))
    # There should be only one boundary left - take the geometry
    boundary_geom = boundaries.geometry[0]

    return boundary_geom
