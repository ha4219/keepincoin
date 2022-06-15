"""
    utils functions
"""

import datetime

def now_to_str() -> str:
    """
        now to str
    """
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d%H%M%S%f")
