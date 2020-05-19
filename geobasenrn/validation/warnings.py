"""Validation checks that result in a warning of some kind. 

Failure of one of these checks *may* not mean the dataset should be rejected from publication, although
depending on the scope of the failure the dataset could still end up being rejected.
"""

import logging

logger = logging.getLogger(__name__)