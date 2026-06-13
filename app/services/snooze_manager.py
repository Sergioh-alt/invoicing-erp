from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.utils.datetime_helpers import parse_iso_safe

def compute_snooze_until(minutes: int) -> datetime:
    return datetime.now().replace(microsecond=0) + timedelta(minutes=minutes)

def snooze_status(snooze_until_iso: Optional[str]) -> Tuple[bool, Optional[str], Optional[int]]:
    dt = parse_iso_safe(snooze_until_iso)
    if not dt:
        return (False, None, None)
    now = datetime.now().replace(microsecond=0)
    if now >= dt:
        return (False, dt.strftime("%H:%M:%S"), 0)
    sec = int((dt - now).total_seconds())
    return (True, dt.strftime("%H:%M:%S"), sec)
