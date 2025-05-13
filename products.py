"""
Module for extracting product information and downloading associated images.

This module contains functions for processing HTML content to extract product names 
and image URLs from tables, generating filenames for images, and saving the images 
to a specified directory. It also includes functionality for downloading missing files 
using multithreading for efficiency.

Functions:
- extract_index_name_image: Extracts product names and image URLs from an HTML table.
- get_image_list: Extracts product information from JSON pages and generates a CSV file.
- get_image_filename: Generates a formatted filename for an image from its ID and URL.
- save_images: Saves images from a list of items to specified filenames.
- save_images_with_threading: Saves images using multiple threads, 
    optionally reading from a CSV file.
- run_with_threads: Executes a function on a list of inputs using multiple threads.
- get_missing_files: Identifies and downloads missing image files based on a reference
     CSV.

Constants:
- IMAGES_PATH: The directory path where images are stored.

Usage Example:
    To extract product data from a JSON file and save the images:
    >>> save_images_with_threading('pages.json', 'products.csv')
"""

import os
import re
import threading

import scrape_tools as st
import modules.my_common_module as mymod


# pylint: disable=W0603

IMAGES_PATH = ""


def extract_index_name_image(html, index):
    """
    Extracts the product name and image URL from an HTML table, and returns them
    along with a running index.

    This function processes the table with the ID 'listItemsTable' in the provided
    HTML content. It searches each row for an image in the first column and a
    product name in the second column, appending them to the result along with
    a zero-based index. The index is incremented for each entry.

    Args:
        html (str): The HTML content containing the table.
        index (int): The starting index for the product rows.

    Returns:
        tuple: A tuple containing:
            - result (list): A list of rows where each row is a list containing
              the index, product name, and image URL.
            - index (int): The updated index after processing the table rows.

    Notes:
        - If the table with ID 'listItemsTable' is not found, the function
          returns an empty list and the input index.
        - Only rows with both an image are included in the result.
    """
    table_id = "listItemsTable"
    table = st.get_table(html, table_id)

    if not table:
        print(f"Table with id '{table_id}' not found.")
        return [], index

    rows = table.find_all("tr")
    result = []

    for row in rows:
        # Find the image URL in the first column (column 0)
        img_tag = row.find("img")
        if img_tag:
            img_url = img_tag["src"]
        else:
            continue

        # Find the product name in the second column (column 1)
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        else:
            name_tag = row.find_all("td")[1].find("a")
            if name_tag:
                product_name = name_tag.get_text(separator=" ").strip()

                # Append the zero-based index, product name, and image URL to the result
                row_result = [index, product_name, img_url]
                result.append(row_result)
                index += 1

    return result, index


def get_image_list(pages_file, output_filename):
    """
    Extract product information and generate a CSV file from the given JSON pages.

    Parameters:
    pages_file (str): Path to the JSON file containing page data.
    output_filename (str): Path for the output CSV file.

    Returns:
    list: A list of extracted items, including IDs, product names, and image URLs.

    Example:
    >>> get_image_list('pages.json', 'output.csv')
    Rows found: 10
    """
    pages = mymod.read_json(pages_file)
    items = [["id", "product", "image_url"]]
    index = 0
    for page in pages:
        result, index = extract_index_name_image(page, index)
        items.extend(result)
    print(f"Rows found: {len(items)}")
    mymod.write_data_to_csv(items, output_filename, mode="w", include_header=True)
    return items


def get_image_filename(row_id, image_url):
    """
    Generate an image filename using a row ID and an image URL.

    Parameters:
    row_id (int or str): Image identifier, formatted as a four-digit number.
    image_url (str): URL of the image, used to extract the file extension.

    Returns:
    str: Formatted filename with prefix and file extension.

    Example:
    >>> get_image_filename(1, 'http://example.com/image.jpg')
    'img_0001.jpg'
    """
    string_format = "img_{:04d}"
    prefix = string_format.format(int(row_id))
    suffix = image_url[image_url.rfind(".") :]
    filename = IMAGES_PATH + prefix + suffix
    return filename


def save_images(items):
    """
    Save images from the given list of items to specified filenames.

    Parameters:
    items (list): A list of items where each item is a list containing
                  at least an ID and an image URL.

    Returns:
    None

    Example:
    >>> save_images([[1, 'Product A', 'http://example.com/image1.jpg'],
    ...               [2, 'Product B', 'image/upload_image.gif']])
    """
    for item in items:
        row_id = item[0]
        if row_id == "id":
            continue
        image_url = item[2]
        if image_url == "image/upload_image.gif":
            continue
        filename = get_image_filename(row_id, image_url)
        st.mymod.download_file(image_url, filename)


def save_images_with_threading(pages_file, reference_file_name, read_from_file=False):
    """
    Save images using multiple threads, either by reading from a CSV file or extracting
    from JSON pages.

    Parameters:
    pages_file (str): Path to the JSON file containing page data.
    reference_file_name (str): Path to the CSV file for reference information.
    read_from_file (bool): If True, reads image data from the CSV file instead of
                           extracting from JSON.

    Example:
    >>> save_images_with_threading('pages.json', 'products.csv')
    """
    global IMAGES_PATH
    IMAGES_PATH = os.path.dirname(reference_file_name) + "/files/"
    if read_from_file:
        items = mymod.read_csv_file(reference_file_name)
    else:
        items = get_image_list(pages_file, reference_file_name)

    run_with_threads(save_images, items[1:], 40)


def run_with_threads(function, input_list, num_threads):
    """Runs the given function on the input list using multiple threads.

    Args:
        function: The function to be executed.
        input_list: The list of inputs to be processed.
        num_threads: The number of threads to use.
    """
    threads = []
    for i in range(num_threads):
        start_index = i * len(input_list) // num_threads
        end_index = (i + 1) * len(input_list) // num_threads
        inputs = input_list[start_index:end_index]
        print(f"Thread {i} : {start_index} - {end_index}")
        thread = threading.Thread(target=function, args=(inputs,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_missing_files(reference_file_name):
    """
    Identifies missing files by comparing the reference file with a list of
    missing files, and then attempts to download the missing files.

    This function reads a 'missing_files.csv' file and a reference file (e.g.,
    'product_images.csv'). It then correlates the missing file entries with the
    reference file based on IDs extracted using a regex pattern. The missing files
    are subsequently processed using threading to download them.

    Args:
        reference_file_name (str): The path to the reference CSV file containing
        product information.

    Globals:
        images_path (str): The directory where images are stored, derived from
        the location of the reference file.
    """
    global IMAGES_PATH
    IMAGES_PATH = os.path.dirname(reference_file_name) + "/files/"

    missing_files = mymod.read_csv_file(
        os.path.dirname(reference_file_name) + "/missing_files.csv"
    )

    # product_images.csv
    ref = mymod.read_csv_file(reference_file_name)
    ref_dict = {row[0]: row[1:] for row in ref}

    download_list = []
    for missing_file in missing_files:
        match = re.search(r"\d+", missing_file[1])
        row_id = str(int(match.group()))
        ref_row = ref_dict[row_id]
        ref_row.insert(0, row_id)
        list.append(ref_row)

    run_with_threads(save_images, download_list, 30)
