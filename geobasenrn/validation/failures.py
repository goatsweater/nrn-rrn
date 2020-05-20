"""Validation checks that result in a failure of some kind. 

Failure of one of these checks generally means the dataset should be rejected from publication.
"""

import calendar
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
        self._validate_year()
        self._validate_month()

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
    
    def _validate_year(self):
        """Check that the year value contains a valid value."""
        # Nothing should be newer than the run date
        this_year = datetime.date.today().year
        # Dates before 1960 predate recordkeeping of the NRN, and are probably an error.
        oldest_year = 1960

        # Make a copy of the data to be manipulated in the checks
        df = self.df.copy()
        # Isolate the year from the rest of the date
        df['year'] = pd.to_numeric(df[self.check_field].str[:4])
        logger.debug("Minimum year in data %s", df['year'].min())
        logger.debug("Maximum year in data %s", df['year'].max())

        # Look for any years that are in the future
        logger.debug("Looking for records newer than %s", this_year)
        in_future = df[df['year'] > this_year]

        if not in_future.empty:
            msg = "Year value cannot be in the future."
            self._record_failure(in_future, self.failure_code, msg)
        
        # Look for years that predate NRN recordkeeping
        logger.debug("Looking for records older than %s", oldest_year)
        too_old = df[df['year'] < oldest_year]
        
        if not too_old.empty:
            msg = f"Year value should probably be before {oldest_year}."
            self._record_failure(too_old, self.failure_code, msg)
    
    def _validate_month(self):
        """Check that all month values are within the range 1-12."""
        lower_bound = 1
        upper_bound = 12

        # Make a copy of the data to be manipulated in the checks
        df = self.df.copy()

        # Drop any records that only have a year
        df = df[df[self.check_field].str.len() > 4]

        # Calculate the month number from the records that have one
        df['month'] = pd.to_numeric(df[self.check_field].str[4:6])

        # Filter the months to any that fall outside the accetable range
        non_compliant = df[(df['month'] < lower_bound) | (df['month'] > upper_bound)]

        if not non_compliant.empty:
            msg = "Invalid month provided for date."
            self._record_failure(non_compliant, self.failure_code, msg)
    
    def _validate_day(self):
        """Check that all day values are within the range appropriate for their month."""
        lower_bound = 1

        # Make a copy of the data to be manipulated in the checks
        df = self.df.copy()

        # Drop any records that don't have a day provided
        df = df[df[self.check_field].str.len() > 6]

        # Extract the month and the day values to their own fields
        df['year'] = pd.to_numeric(df[self.check_field].str[:4])
        df['month'] = pd.to_numeric(df[self.check_field].str[4:6])
        df['day'] = pd.to_numeric(df[self.check_field].str[6:8])

        # There should be no dates less than the lower bound
        non_compliant = df[df['day'] < lower_bound]
        if not non_compliant.empty:
            msg = f"Invalid day of the month - cannot be less than {lower_bound}"
            self._record_failure(non_compliant, self.failure_code, msg)
        
        # Check that the end day does not exceed the number of days in that month
        month_groups = df.groupby('month', sort=False)
        # Iterate through the months, but ignore February
        for month_number in [1,3,4,5,6,7,8,9,10,11,12]:
            # Skip this month if it isn't in the data
            if month_number not in month_groups:
                continue

            upper_bound = calendar.mdays[month_number]
            
            # Get the group data to be processed
            group_data = month_groups.get_group(month_number)

            # Check for any data out of the acceptable range
            non_compliant = group_data[group_data['day'] > upper_bound]
            if not non_compliant.empty:
                msg = f"Invalid day of the month - cannot be more than {upper_bound} for {month_number}"
                self._record_failure(non_compliant, self.failure_code, msg)

        # February could contain a leap year. Break it down by year to check.
        feb_data = month_groups.get_group(2)
        year_groups = feb_data.groupby('year')
        for year_number, year_data in year_groups:
            # February normally has 28 days
            upper_bound = 28
            # If this is a leap year accept 29 days
            if calendar.isleap(year_number):
                upper_bound = 29
            
            # Check for any data with an unacceptable day
            non_compliant = year_data[year_data['day'] > upper_bound]
            if not non_compliant.empty:
                msg = f"Invalid day of the month - cannot be more than {upper_bound} for {month_number}"
                self._record_failure(non_compliant, self.failure_code, msg)
