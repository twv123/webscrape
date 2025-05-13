# pylint: skip-file

# pylint: disable=all


FILE_NAME = "sipl/subpages/12642.html"

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def extract_nested_table_data(nested_table):
    """Extracts data from a nested table."""
    nested_data = []
    for nested_row in nested_table.find_all("tr"):
        nested_row_data = [
            nested_cell.get_text(strip=True)
            for nested_cell in nested_row.find_all(["th", "td"])
        ]
        nested_data.append(nested_row_data)
    return pd.DataFrame(nested_data)

def download_link_old(key, link):
    # filename = sanitize_filename(link.displayed_text)
    filename = link.displayed_text

    # current pdf with preview
    # new_url = get_redirect_url(link.url)
    print(link.url)
    new_url = link.url.replace("\\", "/")
    print("new link: " + new_url)

    st.driver.open(new_url)
    # st.driver.open("https://yarchive.net/")
    # st.driver.close()

    # existing
    download_filename = FILE_DOWNLOAD_DIRECTORY + key + "/" + filename
    # mymod.download_file(new_url, download_filename)
    mymod.move_file("downloaded_files/" + filename, download_filename)
    print(f"Downloaded: {download_filename}")
    print("")



def get_cleaned_table_data(table, filter_by_max_columns=False):
    """Extracts table data cleanly, including nested table data.

    Args:
        table (BeautifulSoup table): The content of a BS table.
        filter_by_max_columns (bool, optional): Flag to enable filtering rows with
            fewer than the maximum number of columns. Defaults to False.

    Returns:
        tuple: (main table data as a DataFrame, nested tables as a dictionary)
    """
    if not table:
        return pd.DataFrame(), {}

    nested_tables = {}
    table_data = []

    for row_index, row in enumerate(table.find_all("tr")):
        row_data = []
        cells = row.find_all(["th", "td"])
        for col_index, cell in enumerate(cells):
            nested_table = cell.find("table")
            if nested_table:
                nested_df = extract_nested_table_data(nested_table)
                nested_tables[(row_index, col_index)] = nested_df
                cell_text = cell.get_text(strip=True) + " (Contains nested table)"
            else:
                cell_text = cell.get_text(strip=True)
            row_data.append(cell_text)
        table_data.append(row_data)

    df = pd.DataFrame(table_data)

    # Filter rows only if the filter flag is set
    if filter_by_max_columns:
        max_columns = df.shape[1]
        filtered = df[df.apply(lambda row: row.count() == max_columns, axis=1)]
    else:
        filtered = df

    return filtered, nested_tables


def get_table(html_content, table_name):
    """Get the table from HTML."""
    if table_name.startswith("#"):
        table_name = table_name[1:]

    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find("table", id=table_name)
    if not table:
        table = soup.find(
            lambda tag: tag.name == "table" and table_name in tag.get("id", "")
        )

    if table:
        return table
    else:
        print(f"Table '{table_name}' not found")
        return None


# Example usage
with open(FILE_NAME, "r") as file:
    html_content = file.read()

table_name = "ListInventoryTable"  # Replace with the actual table ID or partial match
table = get_table(html_content, table_name)
if table:
    main_table_data, nested_tables = get_cleaned_table_data(
        table, filter_by_max_columns=True
    )
    print("Main Table Data:")
    print(main_table_data)
    print("\nNested Tables Data:")
    for key, nested_df in nested_tables.items():
        print(f"Nested table at row {key[0]}, column {key[1]}:")
        print(nested_df)


def download_pdfs_from_table(soup, table_selector, link_column_index, output_folder):
    """
    Downloads PDF files from links within a table in the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The parsed HTML content.
        table_selector (str): CSS selector to identify the table.
        link_column_index (int): Index of the column containing PDF links (0-based).
        output_folder (str): Path to the folder where PDFs will be saved.
    """
    table = soup.select_one(table_selector)
    if not table:
        print("Table not found with the provided selector.")
        return

    for row in table.find_all("tr")[1:]:  # Skip header row
        cells = row.find_all("td")
        if len(cells) <= link_column_index:
            continue

        pdf_url = cells[link_column_index].find("a")["href"]

        # Handle relative URLs by potentially prepending base URL
        if not pdf_url.startswith("http"):
            base_url = soup.find("base")["href"] if soup.find("base") else ""
            pdf_url = f"{base_url}{pdf_url}"

        filename = pdf_url.split("/")[-1]
        filepath = f"{output_folder}/{filename}"

        try:
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            print(f"Downloaded PDF: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")


# Example usage (replace with your actual values)
url = "https://www.example.com/data.html"
table_selector = "table.data-table"
link_column_index = 1  # Assuming PDF links are in the second column (0-based)
output_folder = "downloaded_pdfs"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

download_pdfs_from_table(soup, table_selector, link_column_index, output_folder)


# ==================================================

from bs4 import BeautifulSoup
import requests
import os


def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, "wb") as file:
            file.write(response.content)
        print(f"File downloaded successfully to {destination}")
    else:
        print(f"Failed to download file from {url}")


def download_files_from_table(table, column_index, destination_folder):
    rows = table.find_all("tr")
    for row in rows[1:]:  # Skip the header row if present
        cells = row.find_all("td")
        if column_index < len(cells):
            link = cells[column_index].find("a")
            if link:
                url = link.get("href")
                file_name = os.path.basename(url)
                destination_path = os.path.join(destination_folder, file_name)
                download_file(url, destination_path)
            else:
                print("No link found in this cell.")


# Example usage:
html_content = """
<table id="example_table">
    <tr>
        <th>File Name</th>
        <th>Download Link</th>
    </tr>
    <tr>
        <td>Document 1</td>
        <td><a href="https://example.com/document1.pdf">Download</a></td>
    </tr>
    <tr>
        <td>Document 2</td>
        <td><a href="https://example.com/document2.pdf">Download</a></td>
    </tr>
</table>
"""

soup = BeautifulSoup(html_content, "html.parser")
table_name = "example_table"
table = soup.find("table", id=table_name)
destination_folder = "path/to/save"  # Replace this with your desired destination folder
download_files_from_table(
    table, 1, destination_folder
)  # Assuming the download link is in the second column


# def get_redirect_url(url):
#     fixed_url = url.replace("\\", "/")
#     st.driver.open(fixed_url)
#     new_url = None

#     while new_url != fixed_url:
#         new_url = st.driver.current_url
#         if new_url != fixed_url:
#             return new_url
#     return None
