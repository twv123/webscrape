

import modules.my_common_module as mymod
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

FILE_NAME = "sipl/subpages/12642.html"



# Load the HTML file
with open(FILE_NAME, "r", encoding="utf-8") as file:
    html_content = file.read()






# On Linux, you may need to use `driver.uc_gui_handle_cf()` to successfully bypass a
# Cloudflare CAPTCHA. 

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
            print("Nested Table Headers:", nested_headers)
            print("Nested Table Data Array:", nested_array)
        else:
            row_data = [td.text.strip() for td in row.find_all("td", recursive=False)]
            top_table_data.append(row_data)

    # result = mymod.reshape_and_concatenate(result, table_data[1:])
    top_array = mymod.list_to_numpy_array_same_length(top_table_data)
    print("Top-Level Table Headers:", headers)
    print("Top-Level Table Data Array:", top_array)

    return headers, top_array, nested_tables


headers, top_array, nested_tables = parse_html_to_numpy_array(
    html_content, "ListInventoryTable"
)


def o():
    # Create pandas DataFrames
    main_df = [
        "Product",
        "Alt. Qty",
        "Billed Qty",
        "Packinglist Qty",
        "Received Qty",
        "Unit Cost",
        "Total Cost",
        "Unit Landed Cost",
    ]

    nested_df = [
        "Serial Num",
        "Barcode",
        "Lot",
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
    ]

    # Combine DataFrames if needed
    combined_df = pd.concat([main_df, nested_df], axis=1)

    # Convert to numpy array
    result_array = combined_df.to_numpy()


print("-" * 40)
print("HEADERS")
print(headers)

print("TOP_ARRAY")
print(top_array, nested_tables)
print("NESTED")
print(nested_tables)
