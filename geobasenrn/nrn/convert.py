"""Convert a provider dataset into valid NRN output.

This conversion does not perform validation against any of the incoming data other than mapping values to their NRN
equivalents when a field has a domain applied to it.
"""

import click
import geobasenrn as nrn
import geobasenrn.io as nrnio
from geobasenrn.errors import ConfigurationError
import geopandas as gpd
import logging
import pandas as pd
from pathlib import Path
import tempfile
import yaml

import pprint


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
@click.pass_context
def convert(ctx, previous_vintage, config_files):
    """Convert an input dataset into an NRN pre-release GPKG."""
    # Convert all the source configurations into an options dictionary to be referenced throughout conversion.
    config_paths = [Path(f) for f in config_files]
    source_config = get_source_config(config_paths)
    pprint.pprint(source_config)

    # TODO:
    # 1. download previous vintage - done (provided directly)
    # 2. compile source attributes - done
    # 3. compile target attributes
    # 4. compile domains
    # 5. generate source dataframes - done
    # 6. generate target dataframes
    # 7. apply field mapping
    # 8. recover missing datasets
    # 9. apply domains
    # 10. filter strplaname duplicates
    # 11. repair nid linkages
    # 12. save to output

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
