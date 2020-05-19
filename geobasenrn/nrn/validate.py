"""Validate a dataset against the rules for the NRN."""

import click
import geobasenrn.io as nrnio
from geobasenrn.validation import DataFrameChecker
import geobasenrn.validation.failures as failures

@click.command()
@click.option('-i', '--input', 'infile',
              type=click.Path(dir_okay=False, file_okay=True,
                              resolve_path=True),
              required=True,
              help="Path to the input file.")
@click.pass_context
def validate(ctx, infile):
    """Set up validation."""
    # Retrieve the data from the conversion GPKG.
    logger.debug("Loading GPKG contents from %s", infile)
    dframes = nrnio.get_gpkg_contents(infile)

def validate_junction():
    """Check the junction layer for compliance with the spec."""
    pass

def validate_roadseg():
    """Check the roadseg layer for compliance with the spec."""
    pass