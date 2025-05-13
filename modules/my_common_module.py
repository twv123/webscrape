""" Useful common tools."""

import shutil
import json
import logging
import os
import csv
from datetime import datetime
import inspect
import re
import requests
import numpy as np
import time

CODE_DIRECTORY = "/home/twv123/my_code_projects/python/webscrape/"
ROOT_DIRECTORY = "/mnt/chromeos/removable/easystore/linux_files/"

logger = None


def add_column(data, new_value, header_value=None):
    """
    Adds a new column at the beginning of a NumPy array with a specific value,
    except for the first row which gets a different header value.

    Args:
        data (np.ndarray): The original NumPy array.
        new_value (str): The value to insert in the new column (except for the first row).
        header_value (str): The value to insert in the first row of the new column.

    Returns:
        np.ndarray: The modified NumPy array with the new column.
    """

    # Check if data is empty
    if len(data) == 0:
        return data

    # Broadcast the values for the new column based on data length
    column_values = np.full(len(data), new_value)
    if header_value:
        column_values[0] = header_value
    result = np.column_stack((column_values, data))

    return result


def list_to_numpy_array_same_length(data, pad_value=0):
    """
    Converts a list of rows with variable lengths to a NumPy array with all rows
    having the same (maximum) length, padding shorter rows with the specified value.

    Args:
        data: A list of rows, where each row can be a list, tuple, or other iterable
            containing elements.
        pad_value: The value to use for padding shorter rows. Defaults to 0.

    Returns:
        A NumPy array with the same number of rows as the input list, and all rows
        having the maximum length found in the input data. Shorter rows are padded
        with the specified pad_value.
    """

    # Find the maximum length of any row
    if not data:
        return np.array([])  # Return an empty NumPy array

    max_len = max(len(row) for row in data)

    # Convert each row to a NumPy array and pad with pad_value
    padded_data = [
        np.pad(
            np.array(row),
            (0, max_len - len(row)),
            mode="constant",
            constant_values=pad_value,
        )
        for row in data
    ]

    # Stack the padded rows into a NumPy array
    return np.vstack(padded_data)


def reshape_and_concatenate(arr1, arr2):
    """Reshapes and concatenates two numpy arrays.

    Args:
      arr1: The first numpy array.
      arr2: The second numpy array.

    Returns:
      A concatenated numpy array with the maximum number of columns.
    """

    arr1_cols = arr1.shape[1]
    arr2_cols = arr2.shape[1]

    if arr1_cols == arr2_cols:
        arr1_reshaped = arr1
        arr2_reshaped = arr2
    else:
        max_cols = max(arr1_cols, arr2_cols)

        # Reshape arrays to have the same number of columns
        arr1_reshaped = np.pad(
            arr1, ((0, 0), (0, max_cols - arr1_cols)), mode="constant"
        )
        arr2_reshaped = np.pad(
            arr2, ((0, 0), (0, max_cols - arr2_cols)), mode="constant"
        )

    # Concatenate the reshaped arrays
    return np.concatenate((arr1_reshaped, arr2_reshaped), axis=0)


def get_filename(filepath):
    """
    This function extracts the filename from a given filepath.

    Args:
        filepath: The path to the file.

    Returns:
        The filename without the extension (e.g., "myfile" from "/path/to/myfile.html").
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def download_file(url, destination):
    """Downloads a file from the specified URL and saves it to the given destination path.

    Parameters:
        url (str): The URL from which to download the file.
        destination (str): The path where the downloaded file will be saved.

    Returns:
        True if downloaded the file.
    """
    full_destination = create_full_file_path(destination)
    check_directory(full_destination)
    response = requests.get(url, timeout=8)
    if response.status_code == 200:
        with open(full_destination, "wb") as file:
            file.write(response.content)
            print(f"Written to: {full_destination}")
        return True
    else:
        logger.error(f"Failed to download file (%s)", url)
        return False


def print_now():
    """Print current time."""
    now = datetime.now()
    print(now.strftime("%H:%M:%S"))


def new_logger(caller_file):
    """
    Creates a logger with specified configuration.

    Args:
        caller_file (str): The absolute path of the calling script/module.  Use
        __file__ attribute of the importing script.

    Returns:
        logging.Logger: A configured logger instance.

    Example:
        # Usage in a script/module
        from my_module import new_logger

        if __name__ == "__main__":
            logger = new_logger(__file__)
            logger.info("This is an example log message.")
            logger.warning("Warning: Something might be wrong!")
    """
    global logger  # pylint: disable=W0603
    current_directory = os.path.dirname(caller_file)
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=(current_directory + "/logs.txt"),
    )
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    logger.addHandler(stream_handler)
    return logger


def write_dataframe_to_csv(data, file_path, include_header=False, mode="a"):
    """Write the table data to a CSV file.

    Args:
        data (pandas.DataFrame): The table data to be written to the CSV file.
        file_path (str): The path to the CSV file.
        include_header (bool): Whether to include the column headers in the CSV file.
        mode (str): The mode to open the file ('a' for append, 'w' for overwrite).
    """
    # Create the directory if it doesn't exist
    check_directory(file_path)

    # Determine the header argument based on include_header and mode.
    header = include_header if mode == "w" else False

    # Write the table data to the CSV file.
    # For some reason the header is duplicated into row 1, so skip it always.
    data.iloc[1:].to_csv(file_path, mode=mode, header=header, index=False)
    print(f"Data written to {file_path}")


def create_full_file_path(partial_file_name, parent_directory=ROOT_DIRECTORY):
    """Creates a full file path by replacing date placeholders and adding the root
      directory path.

    Args:
        partial_file_name (str): Partial file name containing date placeholders like
          {%Y}, {%m}, {%d}, {%H}, {%M} etc.

    Returns:
        str: Full file path.
    """

    # Replace {%Y} and other date holders with current datetime.
    def replace_date_items(match):
        placeholder = match.group(1)
        return datetime.now().strftime(placeholder)

    file_name = re.sub(r"\{([^\{ \}]+)\}", replace_date_items, partial_file_name)
    return os.path.join(parent_directory, file_name)


def write_data_to_csv(data, file_name, include_header=False, mode="a", has_header=True):
    """Write data to a CSV file.

    Args:
        data (list): The data to write to the CSV file.
        file_name (str): The name of the CSV file.
        include_header (bool, optional): Whether to include the header row. Defaults to False.
        mode (str, optional): The file mode ('w' for write, 'a' for append). Defaults to "a".

    Returns:
        None
    """

    full_name = create_full_file_path(file_name)

    # Create the directory if it doesn't exist
    check_directory(full_name)

    # Determine the header argument based on include_header and mode.
    if has_header:
        if not include_header or mode == "a":
            new_data = data[1:]
        else:
            new_data = data
    else:
        new_data = data

    # Open the file using the determined mode
    with open(full_name, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        if mode == "w":
            writer.writerows(new_data)
            print(f"CSV file created: {file_name}")
        else:
            writer.writerows(new_data)
            print(f"CSV file appended: {file_name}")


def check_directory(file_name):
    """Create the directory if it doesn't exist."""
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_page(page_content, file_name):
    """Saves the HTML content of a page to a file.

    Args:
        page_content (str): The HTML content of the page.
        file_path (str): The full path (including filename) where the page will be saved.
    """
    full_file_name = create_full_file_path(file_name)
    # Create the directory if it doesn't exist
    check_directory(full_file_name)

    with open(full_file_name, "w", encoding="utf-8") as file:
        file.write(page_content)


def save_json(content, filename):
    destination = create_full_file_path(filename)
    check_directory(destination)
    with open(destination, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
    print(f"JSON saved to file: {destination}")


def read_json(filename):
    full_filename = create_full_file_path(filename)
    with open(full_filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_file_list(directory, qty=None):
    """
    This function retrieves the contents of a specified number of HTML files in a directory.

    Args:
        directory: The path to the directory containing the HTML files.
        qty (optional): The number of files to retrieve content from.
                         Defaults to None (all files).

    Returns:
        A list containing the contents of the requested HTML files,
        or an empty list if no HTML files are found.
    """
    files = []
    processed_count = 0
    directory = create_full_file_path(directory)

    qty_files = len(os.listdir(directory))
    for filename in os.listdir(directory):
        if processed_count < (qty or qty_files):
            print(f"Getting file {processed_count}/{qty_files}...", end="\r")
            filepath = os.path.join(directory, filename)
            # with open(filepath, "r") as f:
            #     html_files.append(f.read())
            files.append(filepath)
            processed_count += 1
    return files


# # Example usage
# file_path = "path/to/output.csv"
# include_header = True  # Set to False if you don't want to include the header

# # First write with header
# write_to_csv(table_data, file_path, include_header=include_header, mode='w')

# # Subsequent writes to append data without header
# include_header = False
# write_to_csv(table_data, file_path, include_header=include_header, mode='a')


def clean_string(string):
    """
    Cleans a string by removing all non-alphanumeric characters and replacing them with underscores.

    Args:
        string (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """

    cleaned_string = ""
    for char in string:
        if char.isalnum():
            cleaned_string += char
        else:
            cleaned_string += "_"
    return cleaned_string


def find_case_insensitive_filename(filename):
    """Finds the actual filename ignoring case."""
    directory = os.path.dirname(filename)
    base_name = os.path.basename(filename).lower()

    # List all files in the directory
    for f in os.listdir(directory):
        if f.lower() == base_name:
            return os.path.join(directory, f)

    # If no match found, return None
    return None


def move_file(filename, new_filename):
    """Moves the specified file to a new name, case-insensitive on file extension."""
    full_filename = create_full_file_path(filename, CODE_DIRECTORY)
    full_new_filename = create_full_file_path(new_filename)
    check_directory(full_new_filename)

    # Use case-insensitive filename search
    full_filename = find_case_insensitive_filename(full_filename) or full_filename

    for i in range(20):
        try:
            shutil.move(full_filename, full_new_filename)
            return
        except FileNotFoundError as e:
            if i == 19:
                # Create a FAIL file after 5 failed attempts
                failed_name = get_failed_filename(full_new_filename)
                check_directory(failed_name)
                with open(failed_name, "w"):
                    pass
                print(f"failed: {failed_name} - err FileNotFoundError: {e}")
            time.sleep(0.5)


def get_failed_filename(path):
    """Extracts the last directory and filename and returns fail file name."""
    head, tail = os.path.split(path)
    last_dir = os.path.basename(head)
    filename = tail.replace("/", "_F-")
    new_filename = "ERRS/" + f"{last_dir}_F-{filename}.FAIL.txt"
    full_fn = create_full_file_path(new_filename)
    return full_fn


def read_csv_file(filename):
    data = []
    filename = create_full_file_path(filename)
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            data.append(list(row))
    return data


def remove_array_dups(array_list):
    """
    Removes duplicate rows from list.
    Example:
        >>> remove_array_dups([['a', 'b'], ['b', 'c'], ['a', 'b']])
        [['a', 'b'], ['b', 'c']]
    """
    unique_data = {tuple(item): item for item in array_list}
    # Convert dictionary back to a list of lists
    result = list(unique_data.values())
    return result


def read_csv_into_dict(filename):
    """Reads a CSV file into a dictionary where the first column is the key."""
    full_filename = create_full_file_path(filename)
    result = {}
    with open(full_filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        # Skip the header row
        # next(reader)
        for row in reader:
            key = row[0]
            value = row[1:]
            result[key] = value
    return result


def is_file_exists(filename):
    """Check if a file exists"""
    full_filename = create_full_file_path(filename)
    return os.path.exists(full_filename)


def download_file_from_url(driver, url, filename):
    """Download file from url."""
    driver.execute_script(
        """
            var link = document.createElement('a');
            link.href = arguments[0];
            link.download = arguments[1];
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """,
        url,
        filename,
    )

    # Poll for the file
    file_path = os.path.join(
        "/home/twv123/my_code_projects/python/webscrape/downloaded_files/", filename
    )
    timeout = 30  # seconds
    start_time = time.time()

    while True:
        if os.path.exists(file_path):
            break
        elif time.time() - start_time > timeout:
            print(
                f"Download timeout: {filename} was not downloaded within {timeout} seconds."
            )
            return False
        time.sleep(0.1)  # Wait before checking again
    return True


def extract_subset_from_dict(target_dict, start=0, end=None):
    """Extracts a subset of items from a dictionary.

    Args:
        mydict: The input dictionary.
        start: The starting index (0-based).
        end: The ending index (exclusive).

    Returns:
        A new dictionary containing the extracted items.
    """
    keys = list(target_dict.keys())
    if end:
        end += 1
    subset_keys = keys[start:end]
    new_dict = {key: target_dict[key] for key in subset_keys}
    return new_dict


def get_unique_items(array, column=0):
    """
    Extracts unique elements from column array of lists.

    Args:
        array: A n-D list.

    Returns:
        A list containing unique elements from column.
    """
    unique_elements = []
    seen_elements = set()

    for row in array:
        element = row[column]
        if element not in seen_elements:
            unique_elements.append(element)
            seen_elements.add(element)

    return unique_elements
