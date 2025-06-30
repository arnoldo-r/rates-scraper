import datetime
import pytz
from config import LOCAL_TZ

def get_current_local_date():
    """Returns the current date in the configured local timezone."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_local = now_utc.astimezone(LOCAL_TZ)
    return now_local.date()