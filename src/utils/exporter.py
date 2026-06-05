"""
exporter.py - Excel export using pandas + openpyxl.

Exports:
  - Per project
  - Per counterparty
  - Full system
"""
import os
import datetime

try:
    import pandas as pd
    _PANDAS_OK = True
except ImportError:
    _PANDAS_OK = False

from ..db.transactions_dao import get_transactions, get_summary
from .jalali_utils import format_jalali_display
from .validators import format_amount

EXPORT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "HesabdarExports")


def _ensure_export_dir():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def _build_dataframe(transactions: list) -> "pd.DataFrame":
    """Convert transaction dicts to a DataFrame with running balance."""
    rows = []
    running_balance = 0.0
    for idx, t in enumerate(transactions, start=1):
        running_balance += t['credit'] - t['debit']
        rows.append({
            'ردیف':        idx,
            'تاریخ':       format_jalali_display(t['jalali_date']),
            'شرح':         t['description'],
            'بدهکار':      t['debit']  if t['debit']  > 0 else '',
            'بستانکار':    t['credit'] if t['credit'] > 0 else '',
            'مانده':       running_balance,
            'پروژه':       t.get('project_name', ''),
            'طرف حساب':    t.get('counterparty_name', '')
        })
    return pd.DataFrame(rows)


def _write_excel(df: "pd.DataFrame", filepath: str, sheet_name: str = "تراکنش‌ها"):
    """Write DataFrame to Excel with basic RTL styling."""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        ws = writer.sheets[sheet_name]

        # Column widths
        col_widths = {'ردیف': 6, 'تاریخ': 14, 'شرح': 35,
                      'بدهکار': 14, 'بستانکار': 14, 'مانده': 16,
                      'پروژه': 20, 'طرف حساب': 20}
        for col_cells in ws.columns:
            header = col_cells[0].value
            ws.column_dimensions[col_cells[0].column_letter].width = \
                col_widths.get(header, 15)

        # RTL sheet direction
        ws.sheet_view.rightToLeft = True

        # Summary rows at bottom
        last_row = ws.max_row + 2
        summary = _summary_from_df(df)
        ws.cell(row=last_row,     column=1, value="جمع کل بدهکار:")
        ws.cell(row=last_row,     column=2, value=summary['total_debit'])
        ws.cell(row=last_row + 1, column=1, value="جمع کل بستانکار:")
        ws.cell(row=last_row + 1, column=2, value=summary['total_credit'])
        ws.cell(row=last_row + 2, column=1, value="مانده نهایی:")
        ws.cell(row=last_row + 2, column=2, value=summary['balance'])


def _summary_from_df(df):
    total_debit  = sum(r for r in df.get('بدهکار', [])  if isinstance(r, (int, float)))
    total_credit = sum(r for r in df.get('بستانکار', []) if isinstance(r, (int, float)))
    return {'total_debit': total_debit, 'total_credit': total_credit,
            'balance': total_credit - total_debit}


def _timestamp_str():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# ─── Public API ──────────────────────────────────────────────────────────────

def export_by_project(project_id: int, project_name: str) -> str:
    """Export all transactions for a project. Returns file path."""
    if not _PANDAS_OK:
        raise RuntimeError("pandas یافت نشد. لطفاً با دستور pip install pandas openpyxl نصب کنید.")
    _ensure_export_dir()
    txs = get_transactions(project_id=project_id)
    df  = _build_dataframe(txs)
    safe_name = project_name.replace('/', '-').replace('\\', '-')
    filepath  = os.path.join(EXPORT_DIR, f"project_{safe_name}_{_timestamp_str()}.xlsx")
    _write_excel(df, filepath, sheet_name=project_name[:31])
    return filepath


def export_by_counterparty(counterparty_id: int, counterparty_name: str) -> str:
    """Export all transactions for a counterparty. Returns file path."""
    if not _PANDAS_OK:
        raise RuntimeError("pandas یافت نشد.")
    _ensure_export_dir()
    txs = get_transactions(counterparty_id=counterparty_id)
    df  = _build_dataframe(txs)
    safe_name = counterparty_name.replace('/', '-').replace('\\', '-')
    filepath  = os.path.join(EXPORT_DIR, f"counterparty_{safe_name}_{_timestamp_str()}.xlsx")
    _write_excel(df, filepath, sheet_name=counterparty_name[:31])
    return filepath


def export_full_system() -> str:
    """Export all transactions across all projects. Returns file path."""
    if not _PANDAS_OK:
        raise RuntimeError("pandas یافت نشد.")
    _ensure_export_dir()
    txs = get_transactions()
    df  = _build_dataframe(txs)
    filepath = os.path.join(EXPORT_DIR, f"full_export_{_timestamp_str()}.xlsx")
    _write_excel(df, filepath, sheet_name="همه تراکنش‌ها")
    return filepath
