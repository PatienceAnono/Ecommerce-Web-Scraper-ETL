import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import time
import re


# -----------------------------------
# 1. SETTINGS
# -----------------------------------

base_url = "https://books.toscrape.com/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
}

request_timeout = 10

delay_between_pages = 1

delay_between_products = 0.5

# Process all 1,000 products
test_product_limit = 1000


# -----------------------------------
# 2. EXTRACT CATALOGUE DATA
# -----------------------------------

products_data = []

current_url = base_url

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
            headers=headers,
            timeout=request_timeout
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
            delay_between_pages
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


# -----------------------------------
# 3. SELECT PRODUCTS FOR DETAIL SCRAPING
# -----------------------------------

products_to_process = products_data[
    :test_product_limit
]

print(
    "\nProducts selected for detail-page test:",
    len(products_to_process)
)


# -----------------------------------
# 4. EXTRACT PRODUCT DETAILS
# -----------------------------------

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
            headers=headers,
            timeout=request_timeout
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

        # Books to Scrape uses:
        # <th> for the field name
        # <td> for the value

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
        delay_between_products
    )


# -----------------------------------
# 5. CREATE DATAFRAME
# -----------------------------------

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


# -----------------------------------
# 6. SAVE RAW DETAIL DATA
# -----------------------------------

raw_file = (
    "data/raw/books_detailed_raw.csv"
)

df.to_csv(
    raw_file,
    index=False
)

print(
    "\nRaw detailed data saved to:",
    raw_file
)


# -----------------------------------
# 7. TRANSFORM
# -----------------------------------

# Catalogue price

df["price"] = (
    df["price"]
    .str.replace(
        "£",
        "",
        regex=False
    )
)

df["price"] = pd.to_numeric(
    df["price"]
)


# Price excluding tax

df["price_excl_tax"] = (
    df["price_excl_tax"]
    .str.replace(
        "£",
        "",
        regex=False
    )
)

df["price_excl_tax"] = pd.to_numeric(
    df["price_excl_tax"]
)


# Price including tax

df["price_incl_tax"] = (
    df["price_incl_tax"]
    .str.replace(
        "£",
        "",
        regex=False
    )
)

df["price_incl_tax"] = pd.to_numeric(
    df["price_incl_tax"]
)


# Tax

df["tax"] = (
    df["tax"]
    .str.replace(
        "£",
        "",
        regex=False
    )
)

df["tax"] = pd.to_numeric(
    df["tax"]
)


# Rating

rating_mapping = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = df["rating"].map(
    rating_mapping
)


# Number of reviews

df["number_of_reviews"] = pd.to_numeric(
    df["number_of_reviews"]
)


# Availability count

df["availability_count"] = pd.to_numeric(
    df["availability_count"]
)


# -----------------------------------
# 8. VALIDATE
# -----------------------------------

print(
    "\n" + "=" * 50
)

print(
    "TRANSFORMED DATA"
)

print(
    "=" * 50
)


print(
    "\nData types:"
)

print(
    df.dtypes
)


print(
    "\nSample transformed data:"
)

print(
    df.head()
)


# -----------------------------------
# 9. DATA QUALITY CHECKS
# -----------------------------------

print(
    "\n" + "=" * 50
)

print(
    "DATA QUALITY REPORT"
)

print(
    "=" * 50
)


# Missing values

print(
    "\nMissing values:"
)

print(
    df.isnull().sum()
)


# Duplicate rows

duplicate_rows = (
    df.duplicated().sum()
)

print(
    "\nDuplicate rows:",
    duplicate_rows
)


# Duplicate product URLs

duplicate_urls = (
    df["product_url"]
    .duplicated()
    .sum()
)

print(
    "Duplicate product URLs:",
    duplicate_urls
)


# Invalid ratings

invalid_ratings = df[
    ~df["rating"].isin(
        [1, 2, 3, 4, 5]
    )
]

print(
    "\nInvalid ratings:",
    len(invalid_ratings)
)


# Invalid prices

invalid_prices = df[
    df["price"] <= 0
]

print(
    "Invalid prices:",
    len(invalid_prices)
)


# Invalid detail prices

invalid_detail_prices = df[
    df["price_incl_tax"] <= 0
]

print(
    "Invalid detail prices:",
    len(invalid_detail_prices)
)


# Missing UPC

missing_upc = df[
    df["upc"].isnull()
]

print(
    "Missing UPC:",
    len(missing_upc)
)


# Missing category

missing_category = df[
    df["category"].isnull()
]

print(
    "Missing category:",
    len(missing_category)
)


# Missing descriptions

missing_description = df[
    df["description"].isnull()
]

print(
    "Missing descriptions:",
    len(missing_description)
)


# Missing images

missing_images = df[
    df["image_url"].isnull()
]

print(
    "Missing image URLs:",
    len(missing_images)
)


print(
    "\n" + "=" * 50
)

print(
    "DATA QUALITY CHECK COMPLETE"
)

print(
    "=" * 50
)


# -----------------------------------
# 10. SAVE PROCESSED DATA
# -----------------------------------

processed_file = (
    "data/processed/books_detailed_clean.csv"
)

df.to_csv(
    processed_file,
    index=False
)

print(
    "\nProcessed detailed data saved to:",
    processed_file
)