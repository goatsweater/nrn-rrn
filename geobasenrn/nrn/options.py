"""Common options and arguments that are shared between commands."""

import click


# Arguments

# Options.
verbose_opt = click.option(
    '--verbose', '-v',
    count=True,
    help="Increase verbosity.")

quiet_opt = click.option(
    '--quiet', '-q',
    count=True,
    help="Decrease verbosity.")

# Coordinate precision option.
precision_opt = click.option(
    '--precision',
    type=int,
    default=-1,
    help="Decimal precision of coordinates.")

# JSON formatting options.
indent_opt = click.option(
    '--indent',
    type=int,
    default=None,
    help="Indentation level for JSON output")
