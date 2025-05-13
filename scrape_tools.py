"""Generic driver class and utilities to scrape SPS site tables """

# pylint: disable=W0718 # broad-exception-caught
# pylint: disable=W0612 # redfined-outer-name

from dataclasses import dataclass
import os

from urllib.parse import urljoin
import numpy as np
import pandas as pd  # pylint: disable=E0401
from seleniumbase import Driver

from bs4 import BeautifulSoup
import modules.my_common_module as mymod
import table_info as ti


# Globals.
driver = None  # pylint: disable=C0103
logger = mymod.new_logger(__file__)
current_logon = None  # pylint: disable=C0103
table_info = ti.table_info  # pylint: disable=W0612 # redfined-outer-name
IS_DEBUGGING = False


@dataclass
class LinkDataClass:
    """Hyperlink data."""

    displayed_text: str
    url: str


@dataclass
class LogonDataClass:
    """Login data."""

    name: str
    url: str
    username: str
    password: str


# Logon info for each subsidiary.
logons = [
    LogonDataClass(
        name="ibs",
        url="http://ibs.stoneprofits.com",
        username="username",
        password="password",
    ),
    LogonDataClass(
        name="dsi",
        url="http://dynamicstone.stoneprofits.com",
        username="user",
        password="password",
    ),
]


def start_browser():
    """Starts a new web browser session."""
    global driver  # pylint: disable=W0603
    driver = Driver(
        uc=True,
        headed=True,
        external_pdf=True,
    )
    driver.ad_block = True
    driver.image_block = True


def open_connection(logon: LogonDataClass = logons[0]):
    """Opens an driver and performs login.

    Args:
        logon (LogonDataClass): The logon information.

    Returns:
        driver: The driver object after successful login.
    """
    global current_logon  # pylint: disable=W0603
    if not driver:
        start_browser()

    logger.info("Opening connection '%s' to url: (%s)", logon.name, logon.url)
    # driver.get("http://google.com")
    # driver.uc_open_with_reconnect(logon.url)
    # driver.uc_open(logon.url)
    driver.open(logon.url)

    timeouts = [10.1, 11.1, 11.2, 9.3, 14.6, 8.2, 7.2, 20]
    for timeout in timeouts:
        driver.uc_open_with_reconnect(logon.url, timeout)
        # driver.get(logon.url)
        # driver.sleep(timeout)
        if driver.is_element_present("#cLogin_dbUsername"):
            break
        else:
            print(
                f"Login element not found after retrying with {timeout} seconds timeout."
            )

    # driver.get(logon.url)

    try:
        driver.is_element_present("#cLogin_dbUsername")
    except Exception:
        logger.exception("Can not logon to site.")

    driver.send_keys("#cLogin_dbUsername", logon.username)
    driver.send_keys("#cLogin_dbPassword", logon.password)
    driver.click("#buttonLogin")

    current_logon = logon
    if not current_logon.url.startswith("http"):
        current_logon.url = "http://" + current_logon.url
    logger.info("Connection opened.")

    return driver


def get_table_links(table, column_number, secondary_column_number=None):
    """Extracts hyperlinks from specified columns of an HTML table.

    Parameters:
        table (BeautifulSoup element): The HTML table element to extract links from.
        column_number (int): The zero-based index of the primary column
            containing hyperlinks.
        secondary_column_number (int, optional): The zero-based index of the
            secondary column containing hyperlinks, if present. If not provided,
            only the primary column is processed.

    Returns:
        tuple: A tuple containing two lists:
            - First list contains LinkDataClass objects with text and URLs
              from the primary column.
            - Second list contains LinkDataClass objects from the secondary
              column, if applicable. If no secondary column is provided, this
              list will contain empty LinkDataClass objects.

    Example Usage:
        # Assume 'soup' is a BeautifulSoup object containing the parsed HTML table.
        table = soup.find("table", {"id": "table_id"})

        # Extract hyperlinks from the third column (index 2).
        primary_links, secondary_links = get_table_links(table, 2)

        # Extract hyperlinks from both the third and fifth columns (indices 2 and 4).
        primary_links, secondary_links = get_table_links(table, 2, 4)

        for link in primary_links:
            print(f"Text: {link.displayed_text}, URL: {link.url}")

        for secondary_link in secondary_links:
            print(f"Secondary Text: {secondary_link.displayed_text}, URL: "
                  f"{secondary_link.url}")
    """

    def __do_cell(link_column):
        """Creates a LinDataClass from a cell."""
        hyperlink = link_column.find("a")
        link_text = hyperlink.contents[0] if hyperlink else ""
        url = hyperlink.get("href") if hyperlink else ""
        link = LinkDataClass(displayed_text=link_text, url=url)
        return link

    print(f"Getting links from table: {table.get('id')}", end="... ")
    result = []
    secondary_result = []
    min_column_count = max(column_number, secondary_column_number or column_number) + 1

    rows = table.find_all("tr")
    for index, row in enumerate(rows[1:], start=1):  # Skip header row.
        cells = row.find_all("td")  # Find all cells in the current row

        if len(cells) <= 1 and index < len(rows) - 1:
            continue  # Skip if no data in cells

        if len(cells) < min_column_count:
            continue

        primary_link = __do_cell(cells[column_number])

        if secondary_column_number:
            secondary_link = __do_cell(cells[secondary_column_number])
        else:
            secondary_link = LinkDataClass(displayed_text="", url="")

        if primary_link.url != "":
            result.append(primary_link)
            secondary_result.append(secondary_link)
        # try:
        #     link = __do_cell(link_column, result)
        #     result.append(link)
        # except Exception as e:
        #     logger.error("Error processing row (%s): %s", index, e)

    return result, secondary_result


# Function to extract Title and URLs from the table
def get_table_links_alternate(html_content, column_number):
    """For example, Quotes is not an iFrame, so files table has no table name."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table by its role
    table = soup.find("table", {"role": "presentation"})
    result = []

    if table:
        # Iterate through the rows (skip the header row)
        rows = table.find_all("tr")[1:]
        for row in rows:
            title_cell = row.find_all("td")[
                column_number
            ]  # Assuming Title is in the second column
            hyperlink = title_cell.find("a")
            if hyperlink:
                title = hyperlink.text.strip()
                url = hyperlink["href"]
                link = LinkDataClass(displayed_text=title, url=url)
                result.append(link)

    return result


def get_root_directory():
    """Returns the root directory of the current script."""
    return os.path.dirname(__file__)


def download_link_file(link, file_prefix):
    """Downloads a file from a link."""
    file_url = get_full_url(link.url)
    file_name = mymod.create_full_file_path(
        "sub_tables/" + file_prefix + "_" + os.path.basename(link.url)
    )
    mymod.download_file(file_url, file_name)


def get_all_table_links(table_info: ti.TableInfoDataClass, pages, column=None):
    """Gets all links for the table, iterating all the pages."""
    if not column:
        column = table_info.column_number

    links = []
    secondary_links = []
    page_count = len(pages) - 1
    counter = -1
    for page in pages:
        counter += 1

        if IS_DEBUGGING and counter > 3:
            break

        print(f"Getting links page {counter} / {page_count}...", end=" ")
        table = get_table(page, table_info.table_id)
        if not table:
            print(f"No table for page {counter}.")
            continue
        page_links, page_secondary_links = get_table_links(
            table, column, table_info.secondary_column_number
        )
        links.extend(page_links)
        secondary_links.extend(page_secondary_links)
        print("done.")
    print("Page links done.")
    return links, secondary_links


def get_full_url(url):
    """Get full url, prepending based on the logon if needed."""
    return urljoin(current_logon.url, url)


def get_all_pages(url, table_id=""):
    """Fetches the content of all pages linked by a "Next" button.

    This function iterates through a series of webpages starting from the provided URL.
    It assumes there's a "Next" button with specific attributes (class and text)
    that leads to the subsequent page.

    Args:
        url (str): The URL of the starting webpage.

    Returns:
        list: A list containing the HTML content of all visited pages.

    Raises:
        Exception: An exception if encountering errors while clicking the "Next" button
                    or retrieving page content.
    """
    driver.open(get_full_url(url))
    result = [driver.page_source]
    xpath = "//a[@class='underline' and text()='Next']"
    if table_id.startswith("#"):
        table_id = table_id[1:]
    table_xpath = f"//*[@id='{table_id}']"
    # /html/body/table/tbody/tr[2]/td/div[6]/div/table[1]/tbody/tr/td[2]/form/a
    counter = 1

    while True:

        try:
            counter += 1
            print(f"Getting page {counter}", end="\r")
            if IS_DEBUGGING and counter > 2:
                return result  # Only do 1 page if debugging.

            # Check for the presence of the "Next" button before clicking
            driver.wait_for_element(xpath, timeout=10)
            print(f"Next button found, checking for table {table_xpath}")
            if table_id:
                driver.wait_for_element(table_xpath, timeout=10)
            driver.click(xpath)
            driver.sleep(4)
            result.append(driver.page_source)
            print(f"Added page html for page {counter}.")

        except Exception:
            logger.info("Error clicking Next button or something...")
            print(Exception)
            break

    print(f"Finished getting all pages for url: {url}")
    return result


def get_subtable_data(table, parent_text, table_key_name):
    """Extracts and prepares subtable data from HTML content.

    Args:
        html (str): The HTML content to extract data from.
        table (TableDataClass): The table object containing metadata about the subtable.
        link (LinkDataClass): The link object containing metadata for the link data.

    Returns:
        np.ndarray: A numpy array containing the subtable data with an added column for
            the link data.
    """
    table_data = get_table_data(table)
    result = add_column(table_data, parent_text, table_key_name)
    return result


def add_column(data, new_value, header_value):
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
    column_values[0] = header_value
    result = np.column_stack((column_values, data))

    return result


def get_subtable_data_all(subtable_name, pages, table_key_name):
    """
    Collects and concatenates data from all instances of a subtable across multiple pages.

    This function processes subtables of type `TableType.DATA`. For each page, it extracts
    the subtable data, ensuring that the relevant parent key (e.g., Purchase Order #) is
    associated with each row.

    Parameters:
        subtable_name (str): The name or identifier of the subtable.
        pages (dict): A dictionary containing page data, with parent keys as the keys and
            HTML content as the values.
        table_key_name (str): The name of the key field in the subtable that links it to
            the parent table.

    Returns:
        pd.DataFrame: A concatenated DataFrame containing all subtable data.

    Raises:
        ValueError: If concatenation fails due to mismatched dimensions.
    """
    # For subtable_info.table_type == ti.TableType.DATA:

    # The 'parent_text' is the parent key. For example, if parent table is
    # Purchase Orders, the displayed text is the PO #.  The 1-to-many rows
    # of the subtable have a column referencing the PO# using the
    # "parent_text".

    counter = 1
    numpages = len(pages)
    result = None
    for parent_text, html_content in pages.items():
        progress_bar = f"Processing item {counter} of {numpages}"
        print(progress_bar, end="\r", flush=True)

        counter += 1

        table = get_table(html_content, subtable_name)
        table_data = get_subtable_data(table, parent_text, table_key_name)
        if table_data.shape[0] == 1:
            continue  # Don't do tables with no data.
        if result is None:
            result = table_data
        else:
            # Join, but drop the header of the new data.
            try:
                result = mymod.reshape_and_concatenate(result, table_data[1:])
            except ValueError as e:
                if "all the input array dimensions" in str(e):
                    msg = (
                        f"Error during concatenation of {parent_text} "
                        "for table {subtable_name}: {e}"
                    )
                    print(msg)
                    print("TABLE DATA:")
                    print(table_data)
                    print("-" * 80)
                    print("RESULT:")
                    print(result)
                    print("=" * 80)
                    logger.exception(msg)
                else:
                    raise  # Re-raise other ValueErrors
    return result


def save_page_source(filename):
    """Save the page html source to a file."""
    mymod.save_page(driver.page_source, filename)


def get_links_html_content(links, tabs, save_dir):
    """Open all links and get HTML content from each page."""

    #     xpath = "//*[@id='tabs']/li[2]/a"
    #     driver.click(xpath)
    #     result.append(get_open_page_content())

    #     xpath = "//*[@id='tabs']/li[3]/a"
    #     driver.click(xpath)
    #     result.append(get_open_page_content())

    # #//*[@id="tabs"]/li[1]/a
    # #//*[@id="tabs"]/li[2]/a
    # #//*[@id="tabs"]/li[3]/a

    pages = {}
    for index, link in enumerate(links):
        if IS_DEBUGGING and index > 10:
            break
        driver.open(get_full_url(link.url))

        if len(tabs) > 0:
            for xpath in tabs:
                driver.click(xpath)
                driver.sleep(1)

        # Create dictionary entry where 'displayed_text' is the text in the
        # parent table that links to the subtable (eg. Purchase Order #).
        # pages[link.displayed_text] = driver.page_source

        filename = save_dir + link.displayed_text + ".html"
        save_page_source(filename)
        print(f"Completed page {index} of {len(links)} :  File: {filename}")
    return pages


# pylint: disable=W0612 # redfined-outer-name
def get_subtable_tabs(table_info: ti.TableInfoDataClass):
    """
    Retrieve the XPath expressions for tabs of all subtables from a given
      TableInfoDataClass.
    """
    result = []
    # pylint: disable=W0612 # unused-variable (subtable_info)
    for subtable_name, subtable_info in table_info.subtables.items():
        result.append(subtable_info.table_tab_xpath)
    return result


# pylint: disable=W0612 # redfined-outer-name
def process_all_subtables(table_name, table_info: ti.TableInfoDataClass, pages):
    """
    Process all subtables of a given table by extracting data or downloading files.

    This function iterates over the subtables in the provided TableInfoDataClass.
    Depending on the type of each subtable (DATA or FILES), it either extracts
    data from the subtable or downloads associated files.

    Parameters:
    table_name (str): The name of the main table being processed.
    table_info (ti.TableInfoDataClass): An instance containing information about
                                         the main table and its subtables.
    pages (dict): A dictionary mapping parent text to HTML content, used for
                  extracting files from the pages.
    """

    # pylint: disable=W0612
    for subtable_name, subtable_info in table_info.subtables.items():
        if subtable_info.table_type == ti.TableType.DATA:
            data = get_subtable_data_all(
                subtable_info.table_id, pages, table_info.table_key_name
            )
            write_subtable_data(subtable_name, data)
            continue

        if subtable_info.table_type == ti.TableType.FILES:
            for parent_text, html_content in pages.items():
                table = get_table(html_content, subtable_info.table_id)
                links, secondary_links = get_table_links(table, 1)
                for link in links:
                    file_prefix = table_info.file_prefix + "/files/" + parent_text + "_"
                    download_link_file(link, file_prefix)
            continue


def write_subtable_data(table_name, subtable_data):
    """Write subtable data to a file."""
    file_name = "sub_tables/" + table_name + "_{%Y%m%d}.csv"
    file_path = mymod.create_full_file_path(file_name)
    mymod.write_data_to_csv(subtable_data, file_path, True, "w")
    logger.info("Wrote subtables for '%s' to file: %s", table_name, file_path)


def get_table_data(table, filter_by_max_columns=False):
    """Extracts table data.

    Args:
        table (BeautifulSoup table): The content of a BS table.
        filter_by_max_columns (bool, optional): Flag to enable filtering rows with
            fewer than the maximum number of columns. Defaults to False.

    Returns:
        np.ndarray: A 2D NumPy array representing the table data.
    """

    if not table:
        return np.array([])

    table_data = []
    for row in table.find_all("tr"):
        row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        table_data.append(row_data)
    df = pd.DataFrame(table_data)

    # Filter rows only if the filter flag is set
    if filter_by_max_columns:
        max_columns = df.shape[1]
        filtered = df[df.apply(lambda row: row.count() == max_columns, axis=1)]
    else:
        filtered = df

    return filtered.to_numpy()


def get_table(html_content, table_name):
    """Get the table from HTML."""
    # bs does not use the hashtag in the element name.
    if table_name.startswith("#"):
        table_name = table_name[1:]

    # soup = BeautifulSoup(html_content, "html.parser")
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find("table", id=table_name)
    # Find the table with a partial match in its ID
    if not table:
        table = soup.find(
            lambda tag: tag.name == "table" and table_name in tag.get("id", "")
        )

    if table:
        return table


def get_table_ids(html_content):
    """
    This function parses HTML content in StringIO format and prints all table IDs.

    Args:
        html_content: A string containing the HTML content in StringIO format.

    Returns:
        None
    """
    soup = BeautifulSoup(html_content, "lxml")
    tables = soup.find_all("table")
    print("Finding tables:...........")
    for table in tables:
        table_id = table.get("id")
        if table_id:
            print(table_id)
