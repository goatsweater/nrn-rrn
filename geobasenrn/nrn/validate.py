"""Validate a dataset against the rules for the NRN."""

import click
import geobasenrn.io as nrnio
from geobasenrn.validation import DataFrameChecker
import geobasenrn.validation.failures as failures
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.option('-i', '--input', 'infile',
              type=click.Path(dir_okay=False, file_okay=True, resolve_path=True),
              required=True,
              help="Path to the input file.")
@click.pass_context
def validate(ctx, infile):
    """Set up validation."""
    # Retrieve the data from the conversion GPKG.
    logger.debug("Loading GPKG contents from %s", infile)
    dframes = nrnio.get_gpkg_contents(infile)

    if 'junction' in dframes:
        results = validate_junction(dframes['junction'])
        report_failures(results)

def report_failures(failure_reports):
    """Send failures to the user."""
    for failure in failure_reports:
        logger.warning(failure)

def validate_junction(df):
    """Check the junction layer for compliance with the spec."""
    # build a list of checks that apply to junctions
    checks = [
        failures.DateCheck(df, 'CREDATE', 'NID'),
        failures.DateCheck(df, 'REVDATE', 'NID')
    ]

    checker = DataFrameChecker('junction', df, checks)
    checker.run_checks()

    # Send back any errors
    for result in checker.results:
        yield result

def validate_roadseg():
    """Check the roadseg layer for compliance with the spec."""
    pass