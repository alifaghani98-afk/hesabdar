"""
projects_dao.py - CRUD operations for the projects table
"""
from .database import get_connection


def get_all_projects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projects ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_project(name, description=''):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO projects (name, description) VALUES (?, ?)",
        (name.strip(), description.strip())
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def update_project(project_id, name, description=''):
    conn = get_connection()
    conn.execute(
        "UPDATE projects SET name=?, description=? WHERE id=?",
        (name.strip(), description.strip(), project_id)
    )
    conn.commit()
    conn.close()


def delete_project(project_id):
    conn = get_connection()
    conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()
