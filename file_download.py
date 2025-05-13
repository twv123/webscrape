"""Functions for downloading files."""

import os
import string
import unicodedata
import re
from bs4 import BeautifulSoup
import scrape_tools as st
import modules.my_common_module as mymod
from quality_check import QualityCheck
import products

CONFIG = None
LOGON_IDS = ["ibs", "dsi"]


class DownloadConfig:
    """
    Represents the configuration settings for the download process.

    Attributes:
        logon_id (int): The logon ID (0 for IBS, 1 for DSI).
        top_level_page_file (str): The path to the top-level pages JSON file.
        sub_pages_directory (str): The directory containing the sub-page htmls.
        table (object): The table configuration object.
            eg 'st.table_info["supplier_invoices"]
        file_download_directory (str):
            The directory where downloaded files will be saved.
        table_url_form (str): The URL form for the table.
        table_url_form_id_name (str): The ID name in the top-level page link.
        file_download_table_name (str): The HTML table ID for the file download table.
        check_files_tab_count (bool):
            Whether to check the number of files in the tab before waiting.
        is_debugging (bool): Whether debugging mode is enabled.
    """

    def __init__(self, table_config_name):
        print("Initializing download configuration...")
        self.table_config_name = table_config_name
        self.table = st.ti.table_info[table_config_name]
        self.__logon_id = 0
        self.table_url_form = self.table.files_table_url_form
        self.table_url_form_id_name = self.table.table_url_form_id_name
        self.file_download_table_name = "tblFiles"
        self.is_debugging = False
        self.use_download_links_csv = False
        self.access_denied_links = []
        self.__set_directorys()

    def set_logon_id(self, logon_id):
        """Set logon id for IBS or DSI."""
        self.__logon_id = logon_id
        self.__set_directorys()
        print(f"Set logon_id to '{LOGON_IDS[self.__logon_id]}'.")

    def get_logon_id(self):
        """Get the logon id being used."""
        return self.__logon_id

    def __set_directorys(self):
        """Directory is for example 'sps_downloads/ibs/customers/'."""
        subsidiary = LOGON_IDS[self.__logon_id]
        self.dir_prefix = f"sps_downloads/{subsidiary}/{self.table_config_name}/"
        self.top_level_page_file = self.dir_prefix + "top_level_pages.json"
        self.sub_pages_directory = self.dir_prefix + "files_tab_html/"
        self.file_download_directory = self.dir_prefix + "files/"

    def __repr__(self):
        """String representation of the configuration for easier debugging."""
        return (
            f"Config(logon_id={self.__logon_id}, "
            f"top_level_page_file='{self.top_level_page_file}', "
            f"sub_pages_directory='{self.sub_pages_directory}', "
            f"table={self.table}, "
            f"file_download_directory='{self.file_download_directory}', "
            f"table_url_form='{self.table_url_form}', "
            f"table_url_form_id_name='{self.table_url_form_id_name}', "
            f"file_download_table_name='{self.file_download_table_name}', "
            f"is_debugging={self.is_debugging})"
        )


def delete_downloaded_files():
    """Deletes all files in the "downloaded_files/" directory."""
    directory = "downloaded_files/"
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def save_links_to_csv(links, filename):
    """Saves link text and url as csv."""
    result = [["display_text", "url"]]
    for link in links:
        t = get_clean_link_displayed_text(link)
        u = link.url
        result.append([t, u])
    mymod.write_data_to_csv(result, filename, True, "w")


def set_table_config(table_config_name):
    """This must be called first."""
    global CONFIG  # pylint: disable=W0603

    CONFIG = DownloadConfig(table_config_name)
    delete_downloaded_files()


def set_debug_flag(debug_flag: bool = False):
    """Set debug flag."""
    CONFIG.is_debugging = debug_flag
    st.IS_DEBUGGING = debug_flag
    print(f"Debug flag set to {debug_flag}.")


def get_debug_flag():
    """Get debug flag."""
    return CONFIG.is_debugging


def save_top_pages():
    """
    Iterates through top level pages (w/ next button),
    then saves pages as JSON to TOP_LEVEL_PAGE_FILE.
    """
    pages = st.get_all_pages(CONFIG.table.url_path, CONFIG.table.table_id)
    mymod.save_json(pages, CONFIG.top_level_page_file)


def get_id_from_url(url):
    """
    Extracts the numeric ID from the URL based on `TABLE_URL_FORM_ID_NAME`.

    When TABLE_URL_FORM_ID_NAME = "userID", then:
    >>> get_id("myurl/page?userID=6789&morethings....")
        6789
    """
    match_string = rf"\?{CONFIG.table_url_form_id_name}=(\d+)"
    match = re.search(match_string, url)
    if match:
        return match.group(1)
    else:
        return None


def start_browser():
    """Open and logon using LOGON_ID = 0 (IBS) or 1 (DSI)."""
    if st.driver:
        return
    st.open_connection(st.logons[CONFIG.get_logon_id()])


def get_sub_page_links(column=None):
    """Gets all links from JSON for the TABLE."""
    if not column:
        column = CONFIG.table.column_number

    print(f"Reading top level json: {CONFIG.top_level_page_file} ...", end=" ...")
    pages = mymod.read_json(CONFIG.top_level_page_file)
    print("done.")
    links, secondary_links = st.get_all_table_links(CONFIG.table, pages, column)

    filename = "links.csv"
    csv_data = [[get_clean_link_displayed_text(link), link.url] for link in links]
    mymod.write_data_to_csv(csv_data, CONFIG.dir_prefix + filename, True, "w")

    filename = "secondary_links.csv"
    csv_data = [
        [get_clean_link_displayed_text(link), link.url] for link in secondary_links
    ]
    mymod.write_data_to_csv(csv_data, CONFIG.dir_prefix + filename, True, "w")

    create_ref_links_file()

    return links


def sanitize_filename(filename):
    """Remove invalid characters and replace spaces with underscores."""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    filename = (
        unicodedata.normalize("NFKD", filename)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )
    return "".join(c for c in filename if c in valid_chars).replace(" ", "_")


def get_clean_link_displayed_text(link: st.LinkDataClass):
    """Gets a string from the link.displayed_text. Sometimes it is HTML, so this fixes that."""
    # pylint: disable=W0702
    try:
        result = link.displayed_text.contents[0]
    except:
        result = str(link.displayed_text)
    return result


def alternate_check_table_exists(html_content):
    """For example, Quotes is not an iFrame, so files table has no table name."""
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", {"role": "presentation"})
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            return True, len(rows) - 1  # Subtracting 1 to account for the header row

    return False, 0


def get_files_url(link):
    """Creates the url link for the file download."""
    link_text = get_clean_link_displayed_text(link)
    url = CONFIG.table_url_form.replace("{id}", str(get_id_from_url(link.url)))
    if "{id_2}" in CONFIG.table_url_form:
        try:
            id2 = str(get_id_from_url(CONFIG.secondary_ref[link_text][1]))
        except:  # pylint: disable=W0702
            print(f"Error getting secondary link for: {link_text} : {url}")
            return
        url = url.replace("{id_2}", id2)

    files_url = st.get_full_url(url)
    return files_url


def iterate_in_chunks(the_array, chunk_size=5):
    """Iterates through a list of links in chunks of a specified size.

    Example usage:
    links = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for chunk in iterate_in_chunks(links, chunk_size=3):
        print(chunk)
    """
    for i in range(0, len(the_array), chunk_size):
        yield the_array[i : i + chunk_size]


def is_blank_tab(url):
    """Check if the tab is empty."""
    return url == "chrome://new-tab-page/" or url == "about:blank"


def __access_denied_error():
    """Iterates all tabs and looks for "<Code>AccessDenied</Code>"""

    for handle in st.driver.window_handles:
        st.driver.switch_to.window(handle)
        page_source = st.driver.page_source
        if page_source:
            if "AccessDenied" in page_source:
                return True

    return False


def clean_tabs():
    """Close all tabs except one blank new tab."""
    # Create empty new tab page.
    st.driver.execute_script("window.open();")
    for handle in st.driver.window_handles:
        st.driver.switch_to.window(handle)
        if is_blank_tab(st.driver.current_url):
            continue
        else:
            st.driver.close()


def remove_prefix(url):
    """Remove the 'http://' or 'https://' from a url."""
    return url.replace("http://", "").replace("https://", "")


def read_links_from_file(filename=""):
    """Creates array of links from csv file."""
    if not filename:
        filename = CONFIG.dir_prefix + "links.csv"
    links_data = mymod.read_csv_file(filename)
    counter = 0
    links = []
    for row in links_data:
        counter += 1
        link = st.LinkDataClass(displayed_text=row[0], url=row[1])
        links.append(link)
        print(f"Created link {counter}...", end="\r")
    return links


def get_child_html_pages(get_links_from_file=False, start_num=0, end_num=None):
    """Gets all the links from top level, and saves html of subpages.

    Args:
    get_links_from_file: If True, reads links from 'links.csv' instead of fetching them
      from the top level URL.
    start_num: The starting index of the links to process.
    end_num: The ending index of the links to process. If None, processes all links.
    """
    print("Getting child html pages....")

    # Reading from file
    if get_links_from_file:
        links = read_links_from_file()
    else:
        links = get_sub_page_links()

    # Secondary links
    if "{id_2}" in CONFIG.table.files_table_url_form:
        __load_secondary_reference()

    clean_tabs()
    counter = 0
    link_count = len(links)

    # Break into chunks.
    chunk_size = 40
    link_chunks = list(iterate_in_chunks(links[start_num:end_num], chunk_size))
    print(f"Doing links in chunks of {chunk_size}. Total chunks: {len(link_chunks)}.")
    for link_chunk in link_chunks:
        if CONFIG.is_debugging and counter > 20:
            break

        st.driver.switch_to.window(st.driver.window_handles[0])

        link_ids = {}
        for link in link_chunk:
            files_url = get_files_url(link)
            abs_index = counter + start_num  # The index in the full list of links.

            if files_url:
                link_ids[remove_prefix(files_url)] = [abs_index, link]
                st.driver.execute_script(f"window.open('{files_url}');")
            counter += 1

        # Iterate the tabs.
        for handle in st.driver.window_handles:
            st.driver.switch_to.window(handle)
            url = st.driver.current_url

            if is_blank_tab(url):
                continue

            abs_index = link_ids[remove_prefix(url)][0]
            link = link_ids[remove_prefix(url)][1]
            clean_link_text = get_clean_link_displayed_text(link)
            print(f"{abs_index} / {link_count}", end=" : ")
            print(f"Parent name={clean_link_text}", end=" : ")
            print(f"Opening: {files_url}", end=" : ")
            html_content = st.driver.page_source

            # Check if the table named "tblFiles" or the alternate version exists,
            # and there are at least 1 row of file downloads.
            table = st.get_table(html_content, CONFIG.file_download_table_name)
            save_html = False
            if not table:
                save_html, num_rows = alternate_check_table_exists(html_content)
            else:
                num_rows = len(table.find_all("tr"))
                if num_rows > 1:
                    save_html = True

            if save_html:
                filename = sanitize_filename(clean_link_text)
                mymod.save_page(
                    html_content, CONFIG.sub_pages_directory + filename + ".html"
                )
                print(f"Saved file: {filename} : Contains {num_rows} files(s).")
            else:
                print(" Empty files table.")

            st.driver.close()

    st.driver.switch_to.window(st.driver.window_handles[0])


def download_link(key, link):
    """Cleans up the link.url and downloads the file"""
    # filename = sanitize_filename(link.displayed_text)
    filename = link.displayed_text
    new_url = link.url.replace("\\", "/")
    download_filename = CONFIG.file_download_directory + key + "/" + filename

    st.driver.execute_script("window.open('');")  # Opens a new tab
    file_downloaded = True

    # Images need specific download.
    # First, they redirect, so the url in the table is not the file.
    # Also, they do not automatically download like pdfs, etc. They are static.
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
        new_url = get_redirect_url(new_url)
        dl_filename = mymod.CODE_DIRECTORY + "downloaded_files/" + filename
        st.mymod.download_file(new_url, dl_filename)
    else:
        st.driver.get(new_url)  # Open the new URL in the new tab

    if __access_denied_error():
        file_downloaded = False
        CONFIG.access_denied_links.append([key, filename, new_url])
        mymod.write_data_to_csv(
            [[key, filename, new_url]],
            CONFIG.dir_prefix + "access_denied_files.csv",
            has_header=False,
        )

        print("ACCESS DENIED ERROR:", end=" ")
    if file_downloaded:
        mymod.move_file("downloaded_files/" + filename, download_filename)
        print("Downloaded.")
    else:
        print(f"File not downloaded: {new_url}")
    __remove_non_blank_tabs()


def get_all_download_links():
    """
    Gets all download links from the subpage html files. If the
      CONFIG.use_download_links_csv = True, reads the file links from
      the file 'dl_links.csv'.
    """
    all_links = {}

    if CONFIG.use_download_links_csv:
        all_links = __convert_link_array_to_dict(__read_link_dict_from_csv())
    else:
        print("Reading list for subpage files...")
        if CONFIG.is_debugging:
            files = mymod.get_file_list(CONFIG.sub_pages_directory, 10)
        else:
            files = mymod.get_file_list(CONFIG.sub_pages_directory)

        counter = 1
        for filename in files:
            file_links = []
            print(f"\rGetting links from file {counter} of {len(files)}...", end="")
            counter += 1

            if CONFIG.is_debugging and counter > 5:
                break

            short_filename = mymod.get_filename(filename)
            with open(filename, "r", encoding="utf-8") as file:
                html_content = file.read()
                table = st.get_table(html_content, CONFIG.file_download_table_name)
                if table:
                    # pylint: disable=unused-variable
                    links, secondary_links = st.get_table_links(
                        table, 1, CONFIG.table.secondary_column_number
                    )
                else:
                    links = st.get_table_links_alternate(html_content, 1)
                file_links.extend(links)
            all_links[short_filename] = file_links
        __save_link_dict_to_csv(all_links)
    return all_links


def download_files_from_key(key, links, counter, qty_keys):
    """Downloads files from a given key and list of links.

    Args:
        key: The key value for the files.
        links: A list of Selenium WebElements representing the links to download.
        counter: The current key index.
        qty_keys: The total number of keys.
    """
    print(f"Key {counter}/{qty_keys}: key_value='{key}'")
    for link in links:
        print(f"Downloading {key}/{link.displayed_text}", end=": ")
        download_link(key, link)


def download_files_from_key_dictionary(links_dict, counter=0, qty_keys=None):
    """Downloads files from all links in a dictionary

    Args:
        links_dict: The input dictionary.
        counter: The starting counter index (default 0).
        qty_keys: Total number of keys being iterated.  Default is the size of
          the links_dict.  Provide a value is this is a subset of larger dict.

    """
    if not qty_keys:
        qty_keys = len(links_dict.items())
    for key, links in links_dict.items():
        counter += 1
        download_files_from_key(key, links, counter, qty_keys)


def process_file_downloads(
    file_dl_key="", start_num=0, end_num=None, all_links=None, skip_prompt=False
):
    """Process file downloads for all the html files saved in SUB_PAGES_DIRECTORY."""
    if not all_links:
        all_links = get_all_download_links()
    print()
    if file_dl_key != "":
        while file_dl_key != "":
            print(f"Getting from file_dl_key='{file_dl_key}'")
            try:
                links = all_links[file_dl_key]
            except:  # pylint: disable=W0702
                print(f"ERROR: no file_dl_key : {file_dl_key} found.")
                return
            download_files_from_key(file_dl_key, links, 1, 1)
            if skip_prompt:
                file_dl_key = ""
            else:
                file_dl_key = input("\n\n\nNext file download key (Enter to quit):")
    else:
        target_links = mymod.extract_subset_from_dict(all_links, start_num, end_num)
        download_files_from_key_dictionary(target_links, start_num, len(all_links))


def __remove_non_blank_tabs():
    handles = st.driver.window_handles
    for handle in handles:
        st.driver.switch_to.window(handle)
        if "about:blank" not in st.driver.current_url:
            st.driver.close()


def get_redirect_url(url):
    """Waits for url to be redirected, returns the new url."""
    fixed_url = url.replace("\\", "/")
    st.driver.open(fixed_url)
    new_url = None
    while new_url != fixed_url:
        new_url = st.driver.current_url
        if new_url != fixed_url:
            handles = st.driver.window_handles
            for handle in handles:
                st.driver.switch_to.window(handle)
                if "about:blank" not in st.driver.current_url:
                    return st.driver.current_url
    return None


def __convert_link_dict_to_array(link_dict):
    array = []
    for key, item in link_dict.items():
        for link in item:
            array.append([key, link.displayed_text, link.url])
    return array


def __convert_link_array_to_dict(link_array):
    link_dict = {}
    for row in link_array:
        key = str(row[0])
        link = st.LinkDataClass(row[1], row[2])
        if key not in link_dict:
            link_dict[key] = []
        link_dict[key].append(link)
    return link_dict


def __save_link_dict_to_csv(link_dict):
    """
    Creates an array of lists from a dictionary of LinkDataClass items and
    saves to file 'dl_links.csv'.
    """
    array = __convert_link_dict_to_array(link_dict)
    mymod.write_data_to_csv(array, CONFIG.dir_prefix + "dl_links.csv", mode="w")


def check_file_quality():
    """Create an instance of QualityCheck with the directory path."""
    quality_check = QualityCheck(mymod.ROOT_DIRECTORY + CONFIG.file_download_directory)
    link_array = __read_link_dict_from_csv()  # Assuming getarray returns the array
    return quality_check.missing_files(link_array)


def print_missing_files():
    """Prints list of missing files."""
    missing_files = mymod.read_csv_file(CONFIG.dir_prefix + "missing_files.csv")
    print("Missing files:")
    print(*missing_files, sep="\n")


def __read_link_dict_from_csv():
    """Reads 'dl_links.csv' and returns the link array."""
    full_filename = mymod.create_full_file_path(CONFIG.dir_prefix + "dl_links.csv")
    data = mymod.read_csv_file(full_filename)
    return data


def __load_secondary_reference():
    """Reads secondary links file and puts in CONFIG.secondary_ref."""
    filename = CONFIG.dir_prefix + "ref_links.csv"

    if mymod.is_file_exists(filename):
        CONFIG.secondary_ref = mymod.read_csv_into_dict(  # pylint: disable=W0201
            filename
        )
        print(f"Read data from {filename}")
    else:
        print(f"ERROR: Secondary reference file is required: {filename}")
        quit()


def create_ref_links_file():
    """
    Generates the 'ref_links.csv' file by correlating data from two CSV files:
    'links.csv' and 'secondary_links.csv'. The first column from 'links.csv'
    and the first two columns from 'secondary_links.csv' are combined into a
    new CSV file called 'ref_links.csv'. This is used for creating the download
    table URL structure.
    """
    links = mymod.read_csv_file(CONFIG.dir_prefix + "links.csv")
    secondary_links = mymod.read_csv_file(CONFIG.dir_prefix + "secondary_links.csv")
    ref_links = []
    for row1, row2 in zip(links, secondary_links):
        new_row = [row1[0]] + row2[:2]
        ref_links.append(new_row)
    mymod.write_data_to_csv(ref_links, CONFIG.dir_prefix + "ref_links.csv", mode="w")


def try_downloading_missed_files():
    """Reads the list of missing files from missing_files.csv and attempts to download
    them.
    """
    key_and_file_names = mymod.read_csv_file(CONFIG.dir_prefix + "missing_files.csv")
    unique_keys = mymod.get_unique_items(key_and_file_names)
    for key in unique_keys:
        process_file_downloads(file_dl_key=str(key), skip_prompt=True)
        print("")


def get_product_images(read_from_file=False):
    """Downloads product images, multithreaded."""
    products.save_images_with_threading(
        CONFIG.top_level_page_file,
        CONFIG.dir_prefix + "product_images.csv",
        read_from_file,
    )


def quality_check_products():
    """Create an instance of QualityCheck with the directory path."""
    quality_check = QualityCheck(mymod.ROOT_DIRECTORY + CONFIG.file_download_directory)

    products.IMAGES_PATH = CONFIG.dir_prefix + "/files/"
    file_list = mymod.read_csv_file(CONFIG.dir_prefix + "product_images.csv")
    key_filename_array = []
    counter = 0
    for row in file_list[1:]:
        counter += 1
        if CONFIG.is_debugging and counter > 10:
            break

        if row[2] == "image/upload_image.gif":
            continue
        filename = os.path.basename(products.get_image_filename(row[0], row[2]))
        key_filename_array.append(["", filename, row[1]])
    return quality_check.missing_files(key_filename_array)


def download_missing_images():
    """Downloads missing image files."""
    # products.images_path = CONFIG.dir_prefix + "/files/"
    products.get_missing_files(CONFIG.dir_prefix + "product_images.csv")
    # products.check_for_missing(CONFIG.dir_prefix + "product_images.csv")
