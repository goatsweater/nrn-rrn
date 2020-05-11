"""Create distributable files of NRN data."""

import click
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import zipfile

import geobasenrn
from geobasenrn.nrn import options


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
    logger = logging.getLogger(__name__)

    # no precision specified, so use the default
    if precision == -1:
        precision = geobasenrn.DEFAULT_PRECISION

    # The name of the driver to use when creating output
    supported_drivers = {
        'gpkg': 'GPKG',
        'shp': 'Shapefile',
        'gml': 'GML',
        'kml': 'KML'
    }
    driver = supported_drivers.get(output_format)

    # The file name for the output
    lang = 'en'.upper()
    source = ctx['province_code'].upper()
    en_filename = f'NRN_{source}_{major_version:02}_{minor_version:02}_GPKG_{lang}.gpkg'
    
    print("Precision:", precision)
    print("Input:", infile)
    print("Output driver:", driver)
    print("Output folder:", out_path)
    print("Output filename:", en_filename)

    self.load_gpkg()
        self.configure_release_version()
        self.compile_french_domain_mapping()
        self.gen_french_dataframes()
        self.gen_output_schemas()
        self.define_kml_groups()
        self.export_temp_data()
        self.export_data()
        self.zip_data()

    # compress the data
    if compress:
        logger.info("Compressing output %s", out_path)
        geobasenrn.io.compress(infile, out_path)