"""List layers that exist for a given NRN dataset."""


import json

import click
from geobasenrn.nrn.options import indent_opt

import fiona


@click.command()
@click.argument('input', required=True)
@indent_opt
@click.pass_context
def ls(ctx, input, indent):
    """List layers in a datasource."""
    result = fiona.listlayers(input)
    click.echo(json.dumps(result, indent=indent))
