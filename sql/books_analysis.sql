-- ============================================================
-- E-COMMERCE WEB SCRAPER & ETL PIPELINE
-- Books to Scrape - SQL Analysis
-- ============================================================
--
-- Database: SQLite
-- Table: books
-- Source: data/processed/books_detailed_clean.csv
--
-- Purpose:
-- Business-style analysis of scraped book catalogue data.
-- ============================================================


-- ============================================================
-- 1. DATASET OVERVIEW
-- ============================================================

SELECT
    COUNT(*) AS total_books,
    COUNT(DISTINCT category) AS categories,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(AVG(rating), 2) AS average_rating,
    ROUND(AVG(availability_count), 2) AS average_stock
FROM books;


-- ============================================================
-- 2. CATEGORY PERFORMANCE
-- ============================================================
-- Excludes source-data category artifacts and very small groups.

SELECT
    category,
    COUNT(*) AS book_count,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(AVG(rating), 2) AS average_rating,
    ROUND(AVG(availability_count), 2) AS average_stock
FROM books
WHERE category NOT IN ('Default', 'Add a comment')
GROUP BY category
HAVING COUNT(*) >= 10
ORDER BY book_count DESC;


-- ============================================================
-- 3. LOW-STOCK BOOKS
-- ============================================================
-- Books with five or fewer units available.

SELECT
    title,
    category,
    price,
    rating,
    availability_count
FROM books
WHERE availability_count <= 5
ORDER BY availability_count ASC, price DESC
LIMIT 20;


-- ============================================================
-- 4. HIGHEST-PRICED BOOKS
-- ============================================================

SELECT
    title,
    category,
    price,
    rating,
    availability_count
FROM books
ORDER BY price DESC
LIMIT 20;


-- ============================================================
-- 5. RATING DISTRIBUTION
-- ============================================================

SELECT
    rating,
    COUNT(*) AS book_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM books),
        2
    ) AS percentage
FROM books
GROUP BY rating
ORDER BY rating;


-- ============================================================
-- 6. INVENTORY RISK SUMMARY
-- ============================================================
-- Identifies the proportion of books with low available stock.

SELECT
    COUNT(*) AS total_books,
    SUM(
        CASE
            WHEN availability_count <= 5 THEN 1
            ELSE 0
        END
    ) AS low_stock_books,
    ROUND(
        SUM(
            CASE
                WHEN availability_count <= 5 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS low_stock_percentage
FROM books;


-- ============================================================
-- 7. HIGH-VALUE / HIGH-RATED BOOKS
-- ============================================================
-- Price threshold uses the 75th percentile calculated in Python.
-- Dataset 75th percentile price: approximately £47.46.
--
-- SQLite does not provide a built-in percentile function,
-- so the threshold was calculated during exploratory analysis.

SELECT
    title,
    category,
    price,
    rating,
    availability_count
FROM books
WHERE price >= 47.46
  AND rating >= 4
  AND category NOT IN ('Default', 'Add a comment')
ORDER BY price DESC;


-- ============================================================
-- 8. CATEGORY INVENTORY COMPARISON
-- ============================================================

SELECT
    category,
    COUNT(*) AS book_count,
    ROUND(AVG(availability_count), 2) AS average_stock,
    MIN(availability_count) AS minimum_stock,
    MAX(availability_count) AS maximum_stock
FROM books
WHERE category NOT IN ('Default', 'Add a comment')
GROUP BY category
HAVING COUNT(*) >= 10
ORDER BY