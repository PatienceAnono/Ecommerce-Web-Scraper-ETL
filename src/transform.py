import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "books_detailed_raw.csv"
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "books_detailed_clean.csv"


def load_data():
    df = pd.read_csv(RAW_FILE)
    return df


def clean_data(df):
    df = df.copy()

    # Remove duplicate products
    df = df.drop_duplicates(subset="product_url")

    # Remove leading/trailing whitespace from text columns
    text_columns = [
        "title",
        "availability",
        "product_url",
        "upc",
        "product_type",
        "category",
        "description",
        "image_url"
    ]

    for column in text_columns:
        df[column] = df[column].str.strip()

    return df

def transform_data(df):
    df = df.copy()

    # Convert currency columns
    currency_columns = [
        "price",
        "price_excl_tax",
        "price_incl_tax",
        "tax"
    ]

    for column in currency_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace("£", "", regex=False)
            .str.strip()
        )
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert rating words to numbers
    rating_mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    df["rating"] = df["rating"].map(rating_mapping)

    # Convert other numeric columns
    numeric_columns = [
        "availability_count",
        "number_of_reviews"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert timestamp
    df["scraped_at"] = pd.to_datetime(
        df["scraped_at"],
        errors="coerce"
    )

    return df


def validate_data(df):
    print("\nData Quality Report")
    print("-" * 40)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nMissing values:")
    print(df.isnull().sum())

    print(f"\nDuplicate product URLs: {df['product_url'].duplicated().sum()}")

    print(f"Invalid ratings: {((df['rating'] < 1) | (df['rating'] > 5)).sum()}")

    print(f"Invalid prices: {(df['price'] <= 0).sum()}")

    return df


def save_data(df):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(PROCESSED_FILE, index=False)

    print(f"\nProcessed data saved to: {PROCESSED_FILE}")


def main():
    print("Starting ETL pipeline...")

    # Extract
    df = load_data()
    print(f"Loaded {len(df)} records.")

    # Transform
    df = clean_data(df)
    df = transform_data(df)

    # Validate
    df = validate_data(df)

    # Load
    save_data(df)

    print("\nETL pipeline completed successfully.")


if __name__ == "__main__":
    main()