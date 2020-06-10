"""A collection of functions that form common operations."""

from geobasenrn.errors import ConfigurationError
from geobasenrn import schema
import logging

logger = logging.getLogger(__name__)

def apply_functions_to_fields(df, target_field, field_schema):
    """Perform some processing on the values to properly extract the values."""
    new_df = df.copy()

    # define each possible type of function
    def replace(col, pattern, replacement, is_regex: bool=True):
        """Perform text replacement on each item in the column. Set is_regex to False to perform exact matches."""
        return col.str.replace(pattern, replacement, is_regex)

    def extract(col, pattern: str, expand: bool=True):
        """Call re.search and extract the first string to match using a regex pattern."""
        return col.str.extract(pattern, expand)
    
    def extract_domain(col, domain_name: str, pattern: str='\b(domain)\b(?!$)', domain_type: str='name', lang: str='en'):
        """Extract a substring based on the values in a domain."""
        if lang.lower() not in ('en', 'fr'):
            raise ConfigurationError(f"Invalid language {lang}")

        if domain_name.lower() not in schema.domains:
            raise ConfigurationError(f"Unknown domain {domain_name}")

        domain = schema.domains.get(domain_name.lower(), {}).get(lang.lower())
        
        # The user can specify if extracting domain "name" values (strings) or "index" values (integers)
        if domain_type == 'name':
            values = '|'.join(domain.keys())
        elif domain_type == 'index':
            values = '|'.join(domain.values())
        
        pattern = pattern.replace('domain', values)
        logger.debug("Extracting text with pattern %r", pattern)

        return col.str.extract(pattern)

    def concat(df, join_cols: [str], join_chars: str=''):
        """Combine multiple columns into a single string."""

        # All the columns need to be strings or this will fail.
        # TODO: verify that all columns are strings before trying.
        return df[join_cols].agg(join_chars.join, axis=1)
    
    def incrementor(col: str, start: int=1, step_size: int=1):
        """Creates an increment across the series, similar to the built-in range() function."""
        return range(start, stop=len(col), step=step_size)
    
    def split(col: str, pat: str=None, n: int=-1, expand=False):
        """Split strings around a given separator/delimiter."""
        return col.str.split(pat, n, expand)

    # Functions that will be applied to entire DataFrames
    df_dispatcher = {
        'concat': concat
    }
    # Functions that will be applied to a Series
    series_dispatcher = {
        'replace': replace,
        'extract': extract,
        'extract_domain': extract_domain
    }

    # Figure out what field is being worked on from the source data
    source_field = field_schema['field']
    if type(source_field) is not str:
        raise ConfigurationError(f'{source_field} must be a single field name string')

    # Call each defined transformation function in series
    new_df[target_field] = new_df[source_field]
    for func_call in field_schema['functions']:
        func_name = func_call['function']
        kwargs = func_call.get('args')

        if func_name in df_dispatcher:
            logger.info("Calling %s on DataFrame", func_name)
            dispatcher = df_dispatcher[func_name]
            new_df[target_field] = dispatcher(new_df, **kwargs)
        elif func_name in series_dispatcher:
            logger.info("Calling %s on column %s", func_name, source_field)
            dispatcher = series_dispatcher[func_name]
            new_df[target_field] = dispatcher(new_df[target_field], **kwargs)
        else:
            # The user could have put anything, so warn them if what they provided is being ignored.
            logger.warning("Ignored function %s on %s. It is not a supported function.", func_name, target_field)
    
    return new_df