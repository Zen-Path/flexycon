import argparse
import os
import shutil
import sqlite3
import time
from datetime import datetime


def extract_schema(db_path, output_file):
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


def generate_diff(old_db, new_db, output_dir):
    """Generate a diff between two databases and save it."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    diff_file = os.path.join(output_dir, f"{timestamp}.sql")

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


def restore_database(base_schema, diffs_dir, output_db):
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


def generate_test_data(output_dir, base_db, num_backups=10):
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

    extract_schema(base_db, os.path.join(output_dir, "base_schema.sql"))

    previous_db = base_db
    for i in range(1, num_backups + 1):
        new_db = os.path.join(output_dir, f"db_{i}.db")
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


def main():
    parser = argparse.ArgumentParser(description="SQLite Diff and Restore Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff_parser = subparsers.add_parser(
        "diff", help="Generate diff between two databases."
    )
    diff_parser.add_argument("old_db", help="Path to the old database.")
    diff_parser.add_argument("new_db", help="Path to the new database.")
    diff_parser.add_argument("output_dir", help="Directory to save the diff.")

    restore_parser = subparsers.add_parser(
        "restore", help="Restore database from base schema and diffs."
    )
    restore_parser.add_argument("base_schema", help="Path to the base schema SQL file.")
    restore_parser.add_argument(
        "diffs_dir", help="Directory containing diff SQL files."
    )
    restore_parser.add_argument("output_db", help="Output database path.")

    test_parser = subparsers.add_parser(
        "generate-test-data", help="Generate test data and diffs."
    )
    test_parser.add_argument(
        "output_dir", help="Directory to save the test databases and diffs."
    )
    test_parser.add_argument("base_db", help="Path to the base database.")
    test_parser.add_argument(
        "--num-backups", type=int, default=10, help="Number of backups to generate."
    )

    args = parser.parse_args()

    if args.command == "diff":
        generate_diff(args.old_db, args.new_db, args.output_dir)
    elif args.command == "restore":
        restore_database(args.base_schema, args.diffs_dir, args.output_db)
    elif args.command == "generate-test-data":
        generate_test_data(args.output_dir, args.base_db, args.num_backups)


if __name__ == "__main__":
    main()
