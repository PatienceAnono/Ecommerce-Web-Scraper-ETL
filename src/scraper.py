import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import time
import re
from pathlib import Path


# -----------------------------------
# 1. SETTINGS
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 10
DELAY_BETWEEN_PAGES = 1
DELAY_BETWEEN_PRODUCTS = 0.5

PRODUCT_LIMIT = 1000

RAW_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "books_detailed_raw.csv"
)


# -----------------------------------
# 2. SCRAPE CATALOGUE
# -----------------------------------

def scrape_catalogue():
    """
    Scrape catalogue pages and return basic product information.
    """

    products_data = []

    current_url = BASE_URL

    scraped_at = datetime.now()

    page_number = 1

    while current_url:

        print(
            f"\nScraping catalogue page {page_number}: "
            f"{current_url}"
        )

        try:
            response = requests.get(
                current_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            print(
                "Status code:",
                response.status_code
            )

            response.raise_for_status()

        except requests.exceptions.RequestException as error:

            print(
                f"Request failed on page {page_number}:"
            )

            print(error)

            break

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        products = soup.select(
            "article.product_pod"
        )

        print(
            "Products found:",
            len(products)
        )

        for product in products:

            title = product.h3.a["title"]

            price = product.select_one(
                ".price_color"
            ).get_text(strip=True)

            availability = product.select_one(
                ".availability"
            ).get_text(strip=True)

            rating_element = product.select_one(
                ".star-rating"
            )

            rating = rating_element.get(
                "class"
            )[1]

            product_url = product.h3.a["href"]

            product_url = urljoin(
                current_url,
                product_url
            )

            product_data = {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "product_url": product_url,
                "scraped_at": scraped_at
            }

            products_data.append(
                product_data
            )

        # -----------------------------------
        # Find next catalogue page
        # -----------------------------------

        next_link = soup.select_one(
            "li.next a"
        )

        if next_link:

            next_url = next_link.get(
                "href"
            )

            current_url = urljoin(
                current_url,
                next_url
            )

            page_number += 1

            time.sleep(
                DELAY_BETWEEN_PAGES
            )

        else:

            current_url = None

    print(
        "\nTotal catalogue records extracted:",
        len(products_data)
    )

    print(
        "Total catalogue pages scraped:",
        page_number
    )

    return products_data


# -----------------------------------
# 3. SCRAPE PRODUCT DETAILS
# -----------------------------------

def scrape_product_details(products_data):
    """
    Scrape detail pages for each product.
    """

    products_to_process = products_data[
        :PRODUCT_LIMIT
    ]

    print(
        "\nProducts selected for detail-page scraping:",
        len(products_to_process)
    )

    detailed_products = []

    for index, product in enumerate(
        products_to_process,
        start=1
    ):

        product_url = product["product_url"]

        print(
            f"\nScraping product "
            f"{index}/{len(products_to_process)}:"
        )

        print(product_url)

        try:

            response = requests.get(
                product_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            print(
                "Status code:",
                response.status_code
            )

            response.raise_for_status()

        except requests.exceptions.RequestException as error:

            print(
                "Product request failed:"
            )

            print(error)

            continue

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        # -----------------------------------
        # PRODUCT INFORMATION TABLE
        # -----------------------------------

        product_table = soup.select(
            "table.table.table-striped tr"
        )

        product_details = {}

        for row in product_table:

            field_cell = row.find("th")

            value_cell = row.find("td")

            if field_cell and value_cell:

                field = field_cell.get_text(
                    strip=True
                )

                value = value_cell.get_text(
                    strip=True
                )

                product_details[field] = value

        # -----------------------------------
        # CATEGORY
        # -----------------------------------

        category_element = soup.select_one(
            "ul.breadcrumb li:nth-of-type(3)"
        )

        if category_element:

            category = category_element.get_text(
                strip=True
            )

        else:

            category = None

        # -----------------------------------
        # DESCRIPTION
        # -----------------------------------

        description_element = soup.select_one(
            "#product_description + p"
        )

        if description_element:

            description = description_element.get_text(
                " ",
                strip=True
            )

        else:

            description = None

        # -----------------------------------
        # IMAGE URL
        # -----------------------------------

        image_element = soup.select_one(
            ".item.active img"
        )

        if image_element:

            image_url = image_element.get(
                "src"
            )

            image_url = urljoin(
                product_url,
                image_url
            )

        else:

            image_url = None

        # -----------------------------------
        # AVAILABILITY COUNT
        # -----------------------------------

        availability_text = product_details.get(
            "Availability"
        )

        if availability_text:

            availability_match = re.search(
                r"\((\d+)\s+available\)",
                availability_text
            )

            if availability_match:

                availability_count = int(
                    availability_match.group(1)
                )

            else:

                availability_count = None

        else:

            availability_count = None

        # -----------------------------------
        # CREATE DETAIL RECORD
        # -----------------------------------

        detailed_product = {
            "title": product["title"],
            "price": product["price"],
            "availability": product["availability"],
            "rating": product["rating"],
            "product_url": product_url,

            "upc": product_details.get(
                "UPC"
            ),

            "product_type": product_details.get(
                "Product Type"
            ),

            "price_excl_tax": product_details.get(
                "Price (excl. tax)"
            ),

            "price_incl_tax": product_details.get(
                "Price (incl. tax)"
            ),

            "tax": product_details.get(
                "Tax"
            ),

            "availability_count": availability_count,

            "number_of_reviews": product_details.get(
                "Number of reviews"
            ),

            "category": category,

            "description": description,

            "image_url": image_url,

            "scraped_at": product["scraped_at"]
        }

        detailed_products.append(
            detailed_product
        )

        time.sleep(
            DELAY_BETWEEN_PRODUCTS
        )

    return detailed_products


# -----------------------------------
# 4. CREATE DATAFRAME
# -----------------------------------

def create_dataframe(detailed_products):
    """
    Convert scraped records into a DataFrame.
    """

    df = pd.DataFrame(
        detailed_products
    )

    print(
        "\n" + "=" * 50
    )

    print(
        "DETAILED DATASET"
    )

    print(
        "=" * 50
    )

    print(
        "\nRows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

    print(
        "\nColumns:"
    )

    print(
        df.columns.tolist()
    )

    print(
        "\nSample data:"
    )

    print(
        df.head()
    )

    return df


# -----------------------------------
# 5. SAVE RAW DATA
# -----------------------------------

def save_raw_data(df):
    """
    Save detailed scraped data as raw CSV.
    """

    RAW_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        RAW_FILE,
        index=False
    )

    print(
        "\nRaw detailed data saved to:",
        RAW_FILE
    )


# -----------------------------------
# 6. MAIN
# -----------------------------------

def main():

    print(
        "Starting web scraping..."
    )

    products_data = scrape_catalogue()

    detailed_products = scrape_product_details(
        products_data
    )

    df = create_dataframe(
        detailed_products
    )

    save_raw_data(
        df
    )

    print(
        "\nWeb scraping completed successfully."
    )


if __name__ == "__main__":
    main()