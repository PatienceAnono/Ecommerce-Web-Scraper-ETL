import sqlite3
import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# File paths
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "books_detailed_clean.csv"
DATABASE_FILE = BASE_DIR / "data" / "books.db"


def load_data():
    """Load the processed CSV file."""
    df = pd.read_csv(PROCESSED_FILE)

    print(f"Loaded {len(df)} records from processed data.")

    return df


def create_database(df):
    """Create SQLite database and load the books table."""

    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_FILE)

    df.to_sql(
        "books",
        conn,
        if_exists="replace",
        index=False
    )

    print(f"Database created: {DATABASE_FILE}")
    print("Table created: books")

    conn.close()


def verify_database():
    """Verify that the books table was created successfully."""

    conn = sqlite3.connect(DATABASE_FILE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM books"
    )

    row_count = cursor.fetchone()[0]

    cursor.execute(
        "PRAGMA table_info(books)"
    )

    columns = cursor.fetchall()

    conn.close()

    print("\nDatabase verification")
    print("-" * 40)
    print(f"Rows in books table: {row_count}")
    print(f"Number of columns: {len(columns)}")


def main():
    print("Starting database load...")

    df = load_data()

    create_database(df)

    verify_database()

    print("\nDatabase load completed successfully.")


if __name__ == "__main__":
    main()