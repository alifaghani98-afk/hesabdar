"""
jalali_utils.py - Persian (Jalali/Shamsi) date helpers.
Requires: jdatetime
"""
import datetime

try:
    import jdatetime
    _JDATETIME_AVAILABLE = True
except ImportError:
    _JDATETIME_AVAILABLE = False


# ─── Public helpers ───────────────────────────────────────────────────────────

def today_jalali() -> str:
    """Return today's Jalali date as 'YYYY-MM-DD'."""
    if _JDATETIME_AVAILABLE:
        jd = jdatetime.date.today()
        return jd.strftime("%Y-%m-%d")
    # Graceful fallback (Gregorian) when jdatetime is missing
    return datetime.date.today().strftime("%Y-%m-%d")


def gregorian_to_jalali(year: int, month: int, day: int) -> str:
    """Convert a Gregorian date to Jalali 'YYYY-MM-DD' string."""
    if _JDATETIME_AVAILABLE:
        jd = jdatetime.date.fromgregorian(year=year, month=month, day=day)
        return jd.strftime("%Y-%m-%d")
    return f"{year:04d}-{month:02d}-{day:02d}"


def jalali_to_gregorian(jalali_str: str):
    """
    Convert Jalali 'YYYY-MM-DD' string to a Gregorian datetime.date.
    Returns None on error.
    """
    try:
        y, m, d = map(int, jalali_str.split('-'))
        if _JDATETIME_AVAILABLE:
            return jdatetime.date(y, m, d).togregorian()
        return datetime.date(y, m, d)
    except Exception:
        return None


def validate_jalali_str(jalali_str: str) -> bool:
    """Return True if the string is a valid Jalali date in 'YYYY-MM-DD' format."""
    try:
        y, m, d = map(int, jalali_str.split('-'))
        if _JDATETIME_AVAILABLE:
            jdatetime.date(y, m, d)
        return True
    except Exception:
        return False


def format_jalali_display(jalali_str: str) -> str:
    """Format 'YYYY-MM-DD' to Persian display string like '۱۴۰۳/۰۵/۱۲'."""
    try:
        y, m, d = jalali_str.split('-')
        return f"{_to_persian_digits(y)}/{_to_persian_digits(m)}/{_to_persian_digits(d)}"
    except Exception:
        return jalali_str


# ─── Internal helpers ─────────────────────────────────────────────────────────

_PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def _to_persian_digits(s: str) -> str:
    return s.translate(_PERSIAN_DIGITS)


JALALI_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد',
    'تیر',     'مرداد',    'شهریور',
    'مهر',     'آبان',     'آذر',
    'دی',      'بهمن',     'اسفند'
]


def month_name(month_number: int) -> str:
    """Return Persian month name for month number 1-12."""
    if 1 <= month_number <= 12:
        return JALALI_MONTHS[month_number - 1]
    return str(month_number)
