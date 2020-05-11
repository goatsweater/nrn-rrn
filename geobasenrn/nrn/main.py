"""Main click group for CLI."""

import logging
from pkg_resources import iter_entry_points
import sys

import click
from click_plugins import with_plugins
from geobasenrn.nrn.options import verbose_opt, quiet_opt


def configure_logging(verbosity):
    """Set the logging level based on verbosity switches."""
    log_level = max(10, 30 - 10 * verbosity)
    logging.basicConfig(stream=sys.stderr, level=log_level)

# valid province codes
prcodes = ['AB', 'BC', 'MB', 'ON', 'NB', 'NL', 'NS', 'NT', 'NU', 'PE', 'QC',
           'SK', 'YT']


@with_plugins(iter_entry_points('geobasenrn.nrn_commands'))
@click.group()
@verbose_opt
@quiet_opt
@click.argument('province',
                type=click.Choice(prcodes, case_sensitive=False))
@click.version_option()
@click.pass_context
def main_group(ctx, verbose, quiet, province):
    """NRN command line interface.
    
    PROVINCE is the code of a province or a territory corresponding to the 
    dataset location. Standard two letter ISO codes are used as the province 
    identifier.
    """
    verbosity = verbose - quiet
    configure_logging(verbosity)
    ctx.obj = {}
    ctx.obj["verbosity"] = verbosity

    if len(province) != 2:
        print("Invalid province code.")
        sys.exit(1)
    ctx.obj['province_code'] = province.lower()
