"""Run validations on data to ensure compliance with the specifications."""

from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

_Result = namedtuple('result', ['layer', 'record', 'field', 'error', 'message'])

class DataFrameChecker:
    """Manage running checks for a pandas DataFrame or geopandas GeoDataFrame and aggregate the results."""

    def __init__(self, identifier, df, checks):
        """Initialize the DataFrame checkers."""
        self.identifier = identifier
        self.df = df
        self.checks = checks
        self.results = []
    
    def __repr__(self):
        """Provide debugging information."""
        return f'DataFrameChecker for {self.identifier}'
    
    def report(self, layer, record_id, column_name, error_code, text):
        """Report an error by storing it in the results list."""
        # If no error code is provided, it should be the first word in the string
        if error_code is None:
            error_code, text = text.split(" ", 1)
        
        result = _Result(layer, record_id, column_name, error_code, text)
        self.results.append(result)
        return error_code
    
    def run_check(self, check, **arguments):
        """Run the check."""
        logger.debug("Running %r with %r", check, arguments)
    
    def run_checks(self):
        """Run checks against the DataFrame."""
        logger.debug("Running all registered checks on %s", self.identifier)
        # run each checker
        for checker in self.checks:
            result = self.run_check(checker)

            # If no problems are reported checkers are expected to report None, otherwise add items to result set.
            if result is not None:
                # Could be a single result or a list of results
                pass

class ValidationCheck:
    """Abstract implementation of a validation check."""
    def __init__(self, df, check_field, id_field=None):
        """Check initializer."""
        self.df = df
        self.check_field = check_field
        self.id_field = id_field
        self.failures = []
    
    def run(self):
        """Method that is called to run the check."""
        return None
    
    def _record_failure(self, df, failure_code, msg):
        """Record items in the supplied DataFrame as a failure."""
        for failure in df.itertuples():
            record_id = failure[self.id_field]
            self.failures.append((record_id, failure_code, msg))