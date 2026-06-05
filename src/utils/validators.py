"""
validators.py - Input validation for transactions and entity forms.
"""
from .jalali_utils import validate_jalali_str


def validate_transaction(debit_str: str, credit_str: str,
                         jalali_date: str, project_id, counterparty_id) -> list:
    """
    Validate transaction inputs.
    Returns a list of Persian error messages (empty = valid).
    """
    errors = []

    # Date
    if not jalali_date or not validate_jalali_str(jalali_date):
        errors.append("تاریخ وارد شده معتبر نیست. فرمت: YYYY-MM-DD")

    # Project & counterparty selection
    if not project_id:
        errors.append("انتخاب پروژه اجباری است.")
    if not counterparty_id:
        errors.append("انتخاب طرف حساب اجباری است.")

    # Amount parsing
    try:
        debit  = float(debit_str)  if debit_str  and debit_str.strip()  else 0.0
        credit = float(credit_str) if credit_str and credit_str.strip() else 0.0
    except ValueError:
        errors.append("مبلغ وارد شده باید عدد باشد.")
        return errors

    if debit < 0 or credit < 0:
        errors.append("مبلغ نمی‌تواند منفی باشد.")

    if debit > 0 and credit > 0:
        errors.append("امکان وارد کردن هر دو مبلغ بدهکار و بستانکار وجود ندارد.")

    if debit == 0 and credit == 0:
        errors.append("حداقل یکی از مبالغ بدهکار یا بستانکار باید وارد شود.")

    return errors


def validate_name_field(value: str, field_label: str = "نام") -> list:
    """Ensure a required name field is not empty."""
    errors = []
    if not value or not value.strip():
        errors.append(f"{field_label} نمی‌تواند خالی باشد.")
    elif len(value.strip()) > 200:
        errors.append(f"{field_label} نباید بیش از ۲۰۰ کاراکتر باشد.")
    return errors


def format_amount(value: float) -> str:
    """Format a float as a Persian-style number string with thousand separators."""
    try:
        return f"{value:,.0f}"
    except Exception:
        return str(value)
