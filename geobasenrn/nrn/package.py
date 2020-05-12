"""Create distributable files of NRN data."""

import click
import geobasenrn as nrn
from geobasenrn.nrn import options
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import tempfile
import zipfile


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

    # Retrieve the data from the conversion GPKG.
    dframes = nrn.io.get_gpkg_contents(infile)

    # Create a temporary workspace within which to create all the data.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Process outputs for the English version of the data.
        if output_format == 'gpkg':
            fname = nrn.io.get_gpkg_filename(identifier, major, minor, 'en')
            out_path = Path(temp_dir).joinpath(fname)
            write_gpkg_output(dframes, out_path)
        
        # Generate French copies of the items in dframes.


        # Process outputs for the French version of the data.


        # Compress the data and delivery it to the desired output folder
        if compress:
            # Get an output compliant filename
            zip_name = 'output.zip'
            if output_format == 'gpkg':
                format_fname = Path(nrn.io.get_gpkg_filename(identifier, major, minor, 'en'))
                zip_fname = f'{format_fname.stem}.zip'
            
            # Compress the items found and write the output to where the user asked
            out_file = out_path.joinpath(zip_fname)
            nrn.io.compress(temp_dir, out_file)



    # TODO: Implement all the processing steps
    # Work should be done within a temporary directory to avoid any possible mixup with data in the current directory.
    # 1. Load the input data, which is the output of the conversion process after being validated
    # 2. Use OGR to build the layers for the chosen output format
    # 3. Output the data to the chosen format for English data
    # 4. Convert the intermediate data to French data
    # 5. Output the French data
    # 6. Compress the outputs
    
    print("Precision:", precision)
    print("Input:", infile)
    print("Output driver:", driver)
    print("Output folder:", out_path)
    print("Output filename:", en_filename)


def write_gpkg_output(dframes: dict, fname: Path) -> Path:
    """Write the contents of dframes out to GeoPackage in the specified work directory.
    
    This creates both a French and English copy of the data.
    """
    pass