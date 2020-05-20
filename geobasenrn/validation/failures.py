"""Validation checks that result in a failure of some kind. 

Failure of one of these checks generally means the dataset should be rejected from publication.
"""

import datetime
import logging
import pandas as pd
from ..validation import ValidationCheck

logger = logging.getLogger(__name__)

class SpeedLimitCheck(ValidationCheck):
    """Check a column for compliance with the speed limit rules."""
    failure_code = 'E101'

    def run(self):
        """Run the analysis to check if the given field complies with speed limit restrictions."""
        self._speed_too_low()
        self._speed_too_high()
        self._incorrect_speed_value()

    def _speed_too_low(self):
        """Speeds must be at least 5 kph."""
        non_compliant = self.df[self.df[self.check_field] < 5]

        # record anything that falls below 5 kph
        if not non_compliant.empty:
            msg = "Speed is below 5 kph"
            self._record_failure(non_compliant, self.failure_code, msg)
    
    def _speed_too_high(self):
        """Speeds must be less than 120 kph."""
        
        non_compliant = self.df[self.df[self.check_field] > 120]
        
        # record anything that falls above 120 kph
        if not non_compliant.empty:
            msg = "Speed is above 120 kph"
            self._record_failure(non_compliant, self.failure_code, msg)
    
    def _incorrect_speed_value(self):
        """Speed values must be divisible by 5, according to the specifications."""
        non_compliant = self.df[self.df[self.check_field].mod(5) == 0]

        # record anything that falls above 120 kph
        if not non_compliant.empty:
            msg = "Speed is not divisible by 5 kph"
            self._record_failure(non_compliant, self.failure_code, msg)

class DateCheck(ValidationCheck):
    """Ensure that a date field complies with the expected values.
    
    Dates can be any of 4, 6, or 8 characters. They aren't real dates, but rather strings that can be 
    reliably converted to real dates by the user.
    """
    failure_code = 'E102'

    def run(self):
        """Analyze the contents of the field to ensure it complies with the product specificaiton."""
        self._validate_not_empty()
        self._validate_length()

        # Make a copy of the data to be manipulated in the checks
        df = self.df.copy()

        # Break the date apart into separate year, month, and day fields.
        df['year'] = df[self.check_field].str[:4]
        df['month'] = df[self.check_field].str[4:6]
        df['day'] = df[self.check_field].str[6:8]

        # Dates that had no month or day now have emptry strings, so those need to be filled in with '01'.
        # The pandas string replace is a regex, so this matches only empty string values.
        df['month'] = df['month'].str.replace('^\s*$','01')
        df['day'] = df['day'].str.replace('^\s*$','01')

        # Assemble the dates into a datetime to perform further checks.
        df['dt'] = pd.to_datetime(df[['year', 'month', 'day']], errors='coerce')

        # Find any records that don't form a valid date
        non_compliant = df[df['dt'].isna()]

        if not non_compliant.empty:
            msg = "Invalid date provided."
            self._record_failure(non_compliant, self.failure_code, msg)
        
        # Continue with other checks for any records that are valid dates
        df = df[df['dt'].notna()]

        self._validate_year(df)

        # If nothing failed, just return None
        if len(self.failures) == 0:
            return None
        
        return self.failures
    
    def _validate_not_empty(self):
        """Dates are not allowed to be empty in the NRN."""
        non_comliant = self.df[self.df[self.check_field].isnull()]

        if not non_comliant.empty:
            msg = "Missing date value"
            self._record_failure(non_comliant, self.failure_code, msg)
    
    def _validate_length(self):
        """Check that dates are all of a valid length."""
        year_only = self.df[self.df[self.check_field].str.len() == 4]
        month_date = self.df[self.df[self.check_field].str.len() == 6]
        full_date = self.df[self.df[self.check_field].str.len() == 8]

        # Extract all the valid dates to find any remaining ones
        correct_dates = pd.concat([year_only, month_date, full_date])[self.check_field].unique()

        # Any dates that are not part of the compliant set have an invalid length
        non_compliant = self.df[~self.df[self.check_field].isin(correct_dates)]

        if not non_compliant.empty:
            msg = "Invalid date length"
            self._record_failure(non_compliant, self.failure_code, msg)
    
    def _validate_year(self, df):
        """Check that the year value contains a valid value."""
        # Nothing should be newer than the run date
        this_year = datetime.datetime.now()

        # Dates before 1960 predate recordkeeping of the NRN, and are probably an error.
        oldest_year = datetime.datetime(1960,1,1)

        # Look for any years that are in the future
        logger.debug("Looking for records newer than %s", this_year)
        in_future = df[df['dt'] > this_year]

        if not in_future.empty:
            msg = "Year value cannot be in the future."
            self._record_failure(in_future, self.failure_code, msg)
        
        # Look for years that predate NRN recordkeeping
        logger.debug("Looking for records older than %s", oldest_year)
        too_old = df[df['dt'] < oldest_year]
        
        if not too_old.empty:
            msg = f"Year value should probably be before {oldest_year}."
            self._record_failure(too_old, self.failure_code, msg)

class DuplicatePointGeometryCheck(ValidationCheck):
    """Look for duplicated points within a geometry."""
    failure_code = 'E103'

    def run(self):
        """Compare the coordinate values of the objects to determine which are duplicated."""
        # Retrieve coordinates as tuples.
        coords = self.df.geometry.map(lambda geom: geom.coords[0])

        # Identify any duplicates as report them all.
        non_compliant = coords.duplicated(keep=False)

        if not non_compliant.empty:
            msg = "Duplicate point geometry found."
            self._record_failure(non_compliant, self.failure_code, msg)
