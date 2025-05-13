""" Scrape data from StoneProfits website. """

import scrape_tools as st
import modules.my_common_module as mymod
import string
import unicodedata
import re


TOP_LEVEL_PAGE_FILE = ""  # For example 'sipl/top_level_pages.json'
SUB_PAGES_DIRECTORY = ""  # For example, 'sipl/subpages/'
TABLE = None  # For example. st.table_info["supplier_invoices"]
#

TOP_LEVEL_PAGE_FILE = "items/top_level_pages.json"
# SUB_PAGES_DIRECTORY = "salesorders/html/files_tab/"
TABLE = st.table_info["items"]

# TABLE_URL_FORM = "fileupload/cUpload.aspx?PartyID={party_id}&Source=Customers"
TABLE_URL_FORM = "fileupload/cUpload.aspx?TransactionID={party_id}&Source=SaleOrder&PresaleID=0&SageOrHausProAPI="
#

table_name = "tblFiles"


def get_id(url):
    match = re.search(r"\?ID=(\d+)", url)
    if match:
        return int(match.group(1))
    else:
        return None


def start_browser():
    logon = st.logons[0]
    st.open_connection(logon)


def save_top_pages():
    pages = st.get_all_pages(TABLE.url_path)
    mymod.save_json(pages, TOP_LEVEL_PAGE_FILE)


def get_sub_page_links():
    pages = mymod.read_json(TOP_LEVEL_PAGE_FILE)
    return st.get_all_table_links(TABLE, pages)


def sanitize_filename(filename):
    # Remove invalid characters and replace spaces with underscores
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = (
        unicodedata.normalize("NFKD", filename)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )

    return "".join(c for c in filename if c in valid_chars).replace(" ", "_")


def get_redirect_url(url):
    fixed_url = url.replace("\\", "/")
    st.driver.open(fixed_url)
    new_url = None

    while new_url != fixed_url:
        new_url = st.driver.current_url
        if new_url != fixed_url:
            return new_url
    return None


def get_child_html_pages():
    links = get_sub_page_links()
    for link in links:
        files_url = st.get_full_url(
            TABLE_URL_FORM.replace("{party_id}", str(get_id(link.url)))
        )
        st.driver.open(files_url)
        html_content = st.driver.page_source
        table = st.get_table(html_content, "tblFiles")
        num_rows = len(table.find_all("tr"))
        if num_rows > 1:
            filename = sanitize_filename(link.displayed_text)
            mymod.save_page(html_content, SUB_PAGES_DIRECTORY + filename + ".html")
            print(f"Saved file: {filename}")


start_browser()
get_child_html_pages()


# print(mymod.clean_string("Wirtz Quality Installations, Inc."))


# for link in links:
#     print(link)


# start_browser()
# st.driver.open(test_table_url)
# html_content = st.driver.page_source


# table = st.get_table(html_content, "tblFiles")
# links = st.get_table_links(table, 1)


# print(links)

# for link in links:
#     print(link.url)
#     filename = sanitize_filename(link.displayed_text)
#     new_url = get_redirect_url(link.url)
#     mymod.download_file(new_url, "testing_dl/" + filename)
