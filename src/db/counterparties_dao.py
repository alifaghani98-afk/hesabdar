"""
counterparties_dao.py - CRUD operations for the counterparties table
"""
from .database import get_connection


def get_all_counterparties():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM counterparties ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_counterparty(counterparty_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM counterparties WHERE id=?", (counterparty_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_counterparty(name, phone='', note=''):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO counterparties (name, phone, note) VALUES (?, ?, ?)",
        (name.strip(), phone.strip(), note.strip())
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def update_counterparty(counterparty_id, name, phone='', note=''):
    conn = get_connection()
    conn.execute(
        "UPDATE counterparties SET name=?, phone=?, note=? WHERE id=?",
        (name.strip(), phone.strip(), note.strip(), counterparty_id)
    )
    conn.commit()
    conn.close()


def delete_counterparty(counterparty_id):
    conn = get_connection()
    conn.execute("DELETE FROM counterparties WHERE id=?", (counterparty_id,))
    conn.commit()
    conn.close()
