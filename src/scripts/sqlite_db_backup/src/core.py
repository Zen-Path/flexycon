import os
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path


def extract_schema(db_path: Path, output_file: Path):
    """Extract the database schema and save it to a file."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql NOT NULL;")
    schema_statements = [row[0] for row in cursor.fetchall()]
    conn.close()

    with open(output_file, "w") as f:
        for statement in schema_statements:
            f.write(f"{statement};\n")

    print(f"Base schema saved to {output_file}")


def generate_diff(old_db: Path, new_db: Path, output_dir: Path):
    """Generate a diff between two databases and save it."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    diff_file = output_dir / f"{timestamp}.sql"

    conn_old = sqlite3.connect(old_db)
    conn_new = sqlite3.connect(new_db)

    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()

    cursor_old.execute("SELECT * FROM users")
    old_data = set(cursor_old.fetchall())

    cursor_new.execute("SELECT * FROM users")
    new_data = set(cursor_new.fetchall())

    added_rows = new_data - old_data

    with open(diff_file, "w") as f:
        for row in added_rows:
            f.write(
                f"INSERT INTO users (id, name, age) VALUES ({row[0]}, '{row[1]}', {row[2]});\n"
            )

    conn_old.close()
    conn_new.close()

    print(f"Diff saved to {diff_file}")


def restore_database(base_schema: Path, diffs_dir: Path, output_db: Path):
    """Restore a database from the base schema and a series of diff files."""
    if os.path.exists(output_db):
        os.remove(output_db)

    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    with open(base_schema) as f:
        cursor.executescript(f.read())

    for diff_file in sorted(os.listdir(diffs_dir)):
        if diff_file.endswith(".sql"):
            with open(os.path.join(diffs_dir, diff_file)) as f:
                cursor.executescript(f.read())
            print(f"Applied {diff_file}")

    conn.commit()
    conn.close()
    print(f"Database restored to {output_db}")


def generate_test_data(output_dir: Path, base_db: Path, num_backups: int = 10):
    """Generate test data with incremental changes and save diffs."""
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Create base database and schema
    if os.path.exists(base_db):
        os.remove(base_db)

    conn = sqlite3.connect(base_db)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);"
    )
    conn.commit()
    conn.close()

    extract_schema(base_db, Path(output_dir, "base_schema.sql"))

    previous_db = base_db
    for i in range(1, num_backups + 1):
        new_db = Path(output_dir, f"db_{i}.db")
        shutil.copy(previous_db, new_db)

        conn = sqlite3.connect(new_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)", (f"User{i}", 20 + i)
        )
        conn.commit()
        conn.close()

        generate_diff(previous_db, new_db, output_dir)
        previous_db = new_db
        time.sleep(0.1)  # Ensure unique timestamps

    print(f"Generated {num_backups} backups with diffs.")
