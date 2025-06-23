
from datetime import datetime, timezone, timedelta
import requests
# Tool to get today's date

def get_todays_date():
    """
    Returns today's date based on Google's server time (UTC+1 for Paris summer).
    """
    response = requests.head('https://www.google.com', timeout=5)
    date_str = response.headers['Date']
    utc_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
    local_date = utc_date.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=1)))  # UTC+1 for Paris summer
    return local_date.date()
