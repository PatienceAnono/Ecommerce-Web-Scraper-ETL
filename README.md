# E-commerce Web Scraper & ETL Pipeline

An end-to-end data engineering and analytics portfolio project that extracts product data from an e-commerce website, transforms and validates the dataset, stores it in SQLite and prepares it for SQL analysis and business insights.

> **Source:** 
>
> [Books to Scrape](https://books.toscrape.com/) — a practice e-commerce website designed for web scraping.

## Project Overview

This project demonstrates a practical **Extract, Transform, Load (ETL)** workflow using Python.

The pipeline collects product and product-detail information from 50 catalogue pages, producing a dataset of **1,000 books and 16 fields per product**.

### Workflow

```text
Books to Scrape
      │
      ▼
┌───────────────┐
│    EXTRACT    │
│  Python +     │
│  Requests +   │
│ BeautifulSoup │
└───────┬───────┘
        │
        ▼
  Raw CSV Dataset
        │
        ▼
┌───────────────┐
│   TRANSFORM   │
│    Pandas     │
│ Cleaning +    │
│ Type Casting  │
└───────┬───────┘
        │
        ▼
 Clean CSV Dataset
        │
        ▼
┌───────────────┐
│     LOAD      │
│    SQLite     │
└───────┬───────┘
        │
        ▼
   books.db
        │
        ├──────────────► SQL Analysis
        │
        └──────────────► Jupyter Analysis
```

## Key Results

| Metric                  |    Result |
| ----------------------- | --------: |
| Catalogue pages scraped |        50 |
| Products extracted      |     1,000 |
| Fields per product      |        16 |
| Categories              |        50 |
| Average price           |    £35.07 |
| Median price            |    £35.98 |
| Average rating          |  2.92 / 5 |
| Average available stock |      8.59 |
| Low-stock products (≤5) | 420 (42%) |
| Duplicate product URLs  |         0 |
| Invalid ratings         |         0 |
| Invalid prices          |         0 |
| Missing descriptions    |         2 |

The two missing descriptions originate from source product pages where a description was not available.

## Data Collected

The scraper collects catalogue and product-detail information including:

* Product title
* Price
* Availability
* Rating
* Product URL
* UPC
* Product type
* Price excluding tax
* Price including tax
* Tax
* Availability count
* Number of reviews
* Category
* Product description
* Image URL
* Scrape timestamp

## Tech Stack

### Web Scraping

* Python
* Requests
* BeautifulSoup
* URL parsing with `urllib.parse`
* Regular expressions

### Data Processing

* Pandas
* Data cleaning
* Data type conversion
* Data validation

### Storage

* SQLite
* CSV

### Analysis

* Jupyter Notebook
* SQL

### Development

* Git
* GitHub
* VS Code

## Project Structure

```text
Ecommerce-Web-Scraper-ETL/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── books.db
│
├── notebooks/
│   └── 01_explore_books.ipynb
│
├── src/
│   ├── __init__.py
│   ├── scraper.py
│   ├── transform.py
│   └── load.py
│
├── sql/
│   └── books_analysis.sql
│
├── dashboard/
│
├── requirements.txt
└── .gitignore
```

> Generated datasets and the SQLite database are excluded from version control through `.gitignore`.

## How the Scraper Works

### 1. Catalogue Extraction

`src/scraper.py` first visits the catalogue and follows the pagination links until all 50 pages have been processed.

For each book, it captures the basic catalogue information and constructs an absolute product URL.

### 2. Product Detail Extraction

The scraper then visits each product page and extracts additional information from the product information table, breadcrumb navigation, description section, and product image.

The scraper is organized into reusable functions:

```python
scrape_catalogue()
scrape_product_details()
create_dataframe()
save_raw_data()
```

This modular structure makes individual stages easier to test and reuse.

## Data Transformation & Validation

The transformation stage uses Pandas to:

* Remove duplicate products
* Strip unnecessary whitespace
* Convert currency strings to numeric values
* Convert rating words such as `Three` into numeric ratings
* Convert inventory and review counts to numeric values
* Convert scrape timestamps to datetime
* Check missing values
* Check duplicate product URLs
* Validate rating ranges
* Validate prices

The cleaned dataset is saved as:

```text
data/processed/books_detailed_clean.csv
```

## Database

The processed dataset is loaded into a SQLite database:

```text
data/books.db
```

with a `books` table containing all 1,000 records and 16 fields.

Example query:

```sql
SELECT
    category,
    COUNT(*) AS book_count,
    ROUND(AVG(price), 2) AS average_price
FROM books
GROUP BY category
ORDER BY book_count DESC;
```

## Analysis

The SQL analysis covers:

1. Dataset overview
2. Category performance
3. Low-stock books
4. Highest-priced books
5. Rating distribution
6. Inventory risk
7. High-value/high-rated books
8. Category inventory comparison
9. Category price comparison
10. Category rating comparison
11. Price-band analysis
12. Stock-band analysis

The Jupyter notebook provides additional exploratory analysis, including distributions, data-quality checks, category analysis, and relationships between price, rating, and inventory.

## Example Insights

A few findings from the dataset:

* **42% of books have 5 or fewer units available**, providing a useful inventory-risk view.
* The average listed price is approximately **£35.07**, while the median is **£35.98**.
* The average product rating is approximately **2.92/5**.
* Price and rating have a very weak linear relationship in this dataset (correlation approximately **0.03**).
* There are **50 source categories** represented in the catalogue.

Because Books to Scrape is a practice dataset, these findings should be treated as demonstrations of the analytical workflow rather than conclusions about the real-world publishing market.

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/PatienceAnono/Ecommerce-Web-Scraper-ETL.git
cd Ecommerce-Web-Scraper-ETL
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the scraper

```bash
python src/scraper.py
```

This extracts the catalogue and product-detail data and saves the raw dataset under `data/raw/`.

### 5. Run the transformation

```bash
python src/transform.py
```

This cleans, transforms, validates, and saves the processed dataset under `data/processed/`.

### 6. Load the database

```bash
python src/load.py
```

This loads the processed dataset into SQLite and verifies the `books` table.

### 7. Explore the analysis

Open:

```text
notebooks/01_explore_books.ipynb
```

and review:

```text
sql/books_analysis.sql
```

## Learning Objectives

This project was built to demonstrate practical skills in:

* Web scraping
* HTML parsing
* Pagination handling
* Data extraction from detail pages
* Data cleaning
* Data validation
* ETL workflow design
* CSV data handling
* SQLite database loading
* SQL analysis
* Exploratory data analysis
* Python project organization
* Git and GitHub workflow

## Portfolio Relevance

This project demonstrates how raw web data can be turned into a structured dataset that is ready for analysis and business reporting.

It complements analytics projects focused on:

* E-commerce performance
* Marketing analytics
* Customer intelligence
* Revenue analysis
* Business dashboards

## Future Enhancements

Potential future improvements include:

* Automated scheduled scraping
* Incremental data collection
* Logging and error monitoring
* Retry handling for failed requests
* Database indexing
* Automated tests
* Pipeline orchestration
* Power BI dashboard integration

These enhancements are intentionally outside the current scope so the core scraping and ETL workflow remains clear and easy to understand.

## Author

**Patience Anono**

Data Analyst | Marketing Analytics & Customer Intelligence

* LinkedIn: 

  https://www.linkedin.com/in/patience-anono-22ab06176/
* Portfolio: 

  https://www.padataanalytics.com/
* GitHub: 

  https://github.com/PatienceAnono
