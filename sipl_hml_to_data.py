""" Scrape data from StoneProfits website. """

import scrape_tools as st
import modules.my_common_module as mymod
from io import StringIO
from seleniumbase import BaseCase
import os
from bs4 import BeautifulSoup
import numpy as np

## this is for IBS
# TOP_LEVEL_PAGE_FILE = "sipl/top_level_pages.json"
# SUB_PAGES_DIRECTORY = "sipl/subpages/"
# OUTPUT_FILE_NAME = "sipltestfreight20240924.csv"

# This is for DSI
TOP_LEVEL_PAGE_FILE = "sipl_dsi/top_level_pages.json"
SUB_PAGES_DIRECTORY = "sipl_dsi/subpages/"
OUTPUT_FILE_NAME = "sipltestfreight_dsi_20240924.csv"


MAIN_COLS = np.array(
    [
        "filename",
        "Product",
        "Col2",
        "Alt. Qty",
        "Billed Qty",
        "Packinglist Qty",
        "Received Qty",
        "Unit Cost",
        "Total Cost",
        "Unit Landed Cost",
        "Col10",
        "Col11",
    ]
)

# FILE_NAME = "sipl/subpages/12642.html"


table = st.table_info["supplier_invoices"]

st.IS_DEBUGGING = False


def start_browser():
    logon = st.logons[0]
    st.open_connection(logon)


def insert_column(array, column_value):
    """Inserts a column at the beginning of an array of arrays.

    Args:
      array: The array of arrays.
      column_value: The value to insert in the new column.

    Returns:
      A new array of arrays with the inserted column.
    """

    return [[column_value] + row for row in array]


def parse_html_to_numpy_array(html_content, top_level_table_id):
    soup = BeautifulSoup(html_content, "html.parser")

    # Parse the top-level table
    top_table = soup.find("table", {"id": top_level_table_id})

    # Extract headers with placeholders for empty headers
    headers = []
    for i, th in enumerate(top_table.find("thead").find_all("th")):
        header_text = th.text.strip()
        if header_text == "":
            header_text = f"Col{i+1}"
        headers.append(header_text)

    # Extract rows
    top_table_data = []
    nested_tables = []

    for row in top_table.find("tbody").find_all("tr", recursive=False):
        # Check for nested table
        nested_table = row.find("table")
        if nested_table:
            nested_headers = []
            for i, th in enumerate(nested_table.find("thead").find_all("th")):
                nested_header_text = th.text.strip()
                if nested_header_text == "":
                    nested_header_text = f"NestedCol{i+1}"
                nested_headers.append(nested_header_text)

            nested_table_data = []
            for nested_row in nested_table.find("tbody").find_all("tr"):
                nested_row_data = [td.text.strip() for td in nested_row.find_all("td")]
                nested_table_data.append(nested_row_data)

            nested_array = np.array(nested_table_data)
            nested_tables.append((nested_headers, nested_array))
            # print("Nested Table Headers:", nested_headers)
            # print("Nested Table Data Array:", nested_array)
        else:
            row_data = [td.text.strip() for td in row.find_all("td", recursive=False)]
            # "Frieght" is a subtotal row that adds no info.
            if not row_data[0].startswith("Freight"):
                top_table_data.append(row_data)

    # result = mymod.reshape_and_concatenate(result, table_data[1:])
    # top_array = mymod.list_to_numpy_array_same_length(top_table_data)
    top_array = top_table_data

    # if len(top_array) > 1:
    #     print("more than one")
    # print("Top-Level Table Headers:", headers)
    # print("Top-Level Table Data Array:", top_array)

    return headers, top_array, nested_tables


def iterate_files():
    all_top_data = []

    files = mymod.get_file_list(SUB_PAGES_DIRECTORY)
    counter = 1
    result = np.array([])
    n = []
    for filename in files:
        print(f"\rProcessing {counter} of {len(files)}", end="")
        counter += 1
        # if counter > 30:
        #     break
        # result = mymod.list_to_numpy_array_same_length(all_top_data, "")
        # result = np.vstack(all_top_data)
        # if counter > 1000:
        #     return np.vstack(all_top_data)
        with open(filename, "r", encoding="utf-8") as file:
            html_content = file.read()
            headers, top_array, nested_tables = parse_html_to_numpy_array(
                # html_content, "ListInventoryTable"
                html_content,
                "ListFreightTable",
            )
            n.extend(nested_tables)
            # Get the base name of the file (including extension)
            file_name_with_ext = os.path.basename(filename)

            # Remove the extension to get just the file name
            short_file_name = file_name_with_ext.split(".")[0]
            new_top_array = insert_column(top_array, short_file_name)
            all_top_data.extend(new_top_array)

            # print("-" * 40)
            # print("HEADERS")
            # print(headers)

            # print("TOP_ARRAY")
            # print(top_array)

            # print("NESTED")
            # print(nested_tables)
    top_result = mymod.list_to_numpy_array_same_length(all_top_data, "")
    return top_result, n


top_data, n = iterate_files()
print(n)

a = np.array(top_data, dtype=str)
a = np.char.replace(a, "\n", " | ")
# a = np.vstack([MAIN_COLS, a])

# final = np.concatenate(MAIN_COLS, a)
# mymod.write_data_to_csv(a, mymod.create_full_file_path("sipltest.csv"), True, "w")
mymod.write_data_to_csv(a, mymod.create_full_file_path(OUTPUT_FILE_NAME), True, "w")
# mydata = np.concatenate(([new_row], mydata), axis=0)


def o():
    # Create pandas DataFrames

    nested_df = [
        "Serial Num",
        "Col2",
        "Barcode",
        "Lot",
        "col4",
        "Supp. Ref",
        "Present Location",
        "Bin",
        "Alt. Qty",
        "Pkg. Qty",
        "Rec. Qty",
        "P",
        "N",
        "D",
        "S",
        "col15",
    ]

    # Combine DataFrames if needed
    combined_df = pd.concat([main_df, nested_df], axis=1)

    # Convert to numpy array
    result_array = combined_df.to_numpy()


# print(pages)
# start_browser()
# save_linked_pages()
# print("DONE!")

# st.process_all_subtables("supplier_invoices", table, pages)


# Completed page %s of %s 233 1566

# https://ibs.stoneprofits.com/vSupplierInvoice.aspx?ID=105182
# ListInventoryTable > tbody > tr:nth-child(2)
