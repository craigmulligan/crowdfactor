from lib.migration import up  
import sqlite3
import pytest

def test_up_success():
    conn = sqlite3.connect(":memory:")
    table_name = "account" 

    up("tests/data/migrations", conn)

    cur = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    [row] = cur.fetchone()
    assert row == table_name 

    cur = conn.execute(f"pragma table_info({table_name});")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    assert "category" in column_names


def test_up_fail():
    conn = sqlite3.connect(":memory:")
    table_name = "account" 
    
    try:
        up("tests/data/migration-fail", conn)
    except sqlite3.OperationalError:
        # These will fail as there is a 
        # syntax issue in the second script.
        pass

    cur = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    [row] = cur.fetchone()
    assert row == table_name 

    # Make sure 2.sql is rolled back.
    cur = conn.execute(f"pragma table_info({table_name});")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    assert "category" not in column_names


def test_fail_up_folder_not_exists():
    conn = sqlite3.connect(":memory:")
    with pytest.raises(FileNotFoundError):
        up("does/not/exist", conn)
