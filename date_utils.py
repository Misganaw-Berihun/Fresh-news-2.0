from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_k_months_before(k):
    """
    Get the date k months before the current date.

    Args:
        k (int): Number of months before the current date.

    Returns:
        datetime: The target date k months before the current date.
    """
    current_date = datetime.today()
    target_date = current_date - relativedelta(months=k)
    return target_date


def is_date_after_or_equal_to_target(str_date, target_date):
    """
    Check if a given date is after or equal to a target date.

    Args:
        str_date (str): The date string to compare in the format
        'Month Day, Year', e.g., 'Jan. 15, 2022' or 'December 25, 2021'.
        target_date (datetime): The target date to compare against.

    Returns:
        bool: True if the given date is after or equal to the target date,
            False otherwise.
    """
    try:
        date_obj = datetime.strptime(str_date, '%b. %d, %Y')
    except ValueError:
        date_obj = datetime.strptime(str_date, '%B %d, %Y')
    return date_obj >= target_date
