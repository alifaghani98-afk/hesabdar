"""
transactions_dao.py - CRUD + aggregation queries for transactions
"""
from .database import get_connection


def get_transactions(project_id=None, counterparty_id=None):
    """
    Fetch transactions with optional filters.
    Returns list of dicts with joined project/counterparty names.
    """
    conn = get_connection()
    base = """
        SELECT
            t.id,
            t.project_id,
            t.counterparty_id,
            t.jalali_date,
            t.description,
            t.debit,
            t.credit,
            p.name AS project_name,
            c.name AS counterparty_name
        FROM transactions t
        JOIN projects       p ON p.id = t.project_id
        JOIN counterparties c ON c.id = t.counterparty_id
    """
    conditions, params = [], []
    if project_id is not None:
        conditions.append("t.project_id = ?")
        params.append(project_id)
    if counterparty_id is not None:
        conditions.append("t.counterparty_id = ?")
        params.append(counterparty_id)
    if conditions:
        base += " WHERE " + " AND ".join(conditions)
    base += " ORDER BY t.jalali_date, t.id"
    rows = conn.execute(base, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction(transaction_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM transactions WHERE id=?", (transaction_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_transaction(project_id, counterparty_id, jalali_date,
                       description, debit, credit):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO transactions
           (project_id, counterparty_id, jalali_date, description, debit, credit)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (project_id, counterparty_id, jalali_date,
         description.strip(), float(debit), float(credit))
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def update_transaction(transaction_id, project_id, counterparty_id,
                       jalali_date, description, debit, credit):
    conn = get_connection()
    conn.execute(
        """UPDATE transactions
           SET project_id=?, counterparty_id=?, jalali_date=?,
               description=?, debit=?, credit=?
           WHERE id=?""",
        (project_id, counterparty_id, jalali_date,
         description.strip(), float(debit), float(credit), transaction_id)
    )
    conn.commit()
    conn.close()


def delete_transaction(transaction_id):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()


def get_summary(project_id=None, counterparty_id=None):
    """Return dict with total_debit, total_credit, balance."""
    conn = get_connection()
    query = "SELECT COALESCE(SUM(debit),0), COALESCE(SUM(credit),0) FROM transactions"
    conditions, params = [], []
    if project_id is not None:
        conditions.append("project_id = ?")
        params.append(project_id)
    if counterparty_id is not None:
        conditions.append("counterparty_id = ?")
        params.append(counterparty_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    row = conn.execute(query, params).fetchone()
    conn.close()
    total_debit  = row[0]
    total_credit = row[1]
    return {
        'total_debit':  total_debit,
        'total_credit': total_credit,
        'balance':      total_credit - total_debit
    }


def get_all_summaries_by_project():
    """Return list of {project_id, project_name, total_debit, total_credit, balance}."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.name,
               COALESCE(SUM(t.debit),0)  AS total_debit,
               COALESCE(SUM(t.credit),0) AS total_credit
        FROM projects p
        LEFT JOIN transactions t ON t.project_id = p.id
        GROUP BY p.id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'project_id':    r[0],
            'project_name':  r[1],
            'total_debit':   r[2],
            'total_credit':  r[3],
            'balance':       r[3] - r[2]
        })
    return result


def get_all_summaries_by_counterparty():
    """Return list of {counterparty_id, counterparty_name, total_debit, total_credit, balance}."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.id, c.name,
               COALESCE(SUM(t.debit),0)  AS total_debit,
               COALESCE(SUM(t.credit),0) AS total_credit
        FROM counterparties c
        LEFT JOIN transactions t ON t.counterparty_id = c.id
        GROUP BY c.id
        ORDER BY c.name
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'counterparty_id':   r[0],
            'counterparty_name': r[1],
            'total_debit':       r[2],
            'total_credit':      r[3],
            'balance':           r[3] - r[2]
        })
    return result
