from bs4 import BeautifulSoup
import scrape_tools as st
import modules.my_common_module as mymod
from seleniumbase import SB
import time
import subprocess

from seleniumbase import BaseCase
from seleniumbase import Driver


st.start_browser()

# URL of the image to download
image_url = "https://seleniumbase.github.io/other/sample_line_chart.png"

# Open the image URL directly
st.driver.get(image_url)

# Download the image file
st.driver.download_file(image_url, "mytest/")

# Optionally, confirm the download by checking file in the download folder
print("File download initiated successfully!")

quit()

cmd = [
    "python3",
    "file_download_main.py",
    "--debug",
    "--table_config",
    "opportunities",
    "--start_num",
    "1140",
]
subprocess.run(cmd)
quit()


# Total pages
# xpath: //*[@id="TotalPages_ListOpportunities"]


# with SB(uc=True, test=True) as sb:
#     url = "https://wildbet.gg/"
#     sb.driver.uc_open_with_reconnect(url, 20)

urls = [
    "https://sjmulder.nl/en/textonly",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.amazon.com",
    "https://www.wikipedia.org",
]


def clean_tabs():
    """Close all tabs except one blank new tab."""
    # Create empty new tab page.
    print("----------------clean_tabs()-----------")
    st.driver.execute_script(f"window.open();")
    print(f"handle[0] : {st.driver.window_handles[0]}")
    for handle in st.driver.window_handles:
        st.driver.switch_to.window(handle)
        print(f"{handle} : {st.driver.current_url}")
        if (
            st.driver.current_url == "chrome://new-tab-page/"
            or st.driver.current_url == "about:blank"
        ):
            continue

        print(f"closing {handle}: {st.driver.current_url}")
        st.driver.close()
    print(f"handle[0] : {st.driver.window_handles[0]}")


st.start_browser()
st.driver.open("https://sjmulder.nl")
clean_tabs()

for url in urls:
    st.driver.execute_script(f"window.open('{url}');")

# Iterate over each tab
for handle in st.driver.window_handles:
    st.driver.switch_to.window(handle)
    print(f"{handle} : url : {st.driver.current_url}")
    if st.driver.current_url == "chrome://new-tab-page/":
        continue

    if st.driver.current_url == "about:blank":
        continue
    # Wait for the page to finish loading
    st.driver.sleep(1)
    st.driver.close()

print(f"handle[0] : {st.driver.window_handles[0]}")
print("closed all tabs")
st.driver.switch_to.window(st.driver.window_handles[0])
# st.driver.open("http://bing.com")
st.driver.execute_script("window.open('https://sjmulder.nl');")

time.sleep(5)

st.driver.sleep(10)
quit()

quit()
import threading
import time


def download_missing_pages():
    opps = [
        "10149",
        "10284",
        "10473",
        "10479",
        "10511",
        "10581",
        "10586",
        "10594",
        "10662",
        "10706",
        "10709",
        "10720",
        "10791",
        "10818",
        "10904",
        "11137",
        "11147",
        "11189",
        "11223",
        "11238",
        "11279",
        "11286",
        "11435",
        "11441",
        "11521",
        "11746",
        "11801",
        "11990",
        "12027",
        "12061",
        "12107",
        "12157",
        "12453",
        "12454",
        "12498",
        "12562",
        "12670",
        "12798",
        "12819",
        "12883",
        "12924",
        "13082",
        "13109",
        "13169",
        "13253",
        "13264",
        "6267",
        "7280",
    ]
    st.open_connection(st.logons[0])
    st.driver.get("https://ibs.stoneprofits.com/")
    all_links = []
    for search_value in opps:
        url = f"https://ibs.stoneprofits.com/listOpportunities.aspx?list=ListOpportunities&q=&q1=&q2=&q3=&q4=&q5=&q6=&q7=&q8=&q9=&q10=&q11=&q12=&q13=&q14=&q15=&q16=&q17=&q18=&q19=&q20=&q21=&q22=&q23=&q24=&q25=&tab=0&sort=ID&order=DESC&searchBy=TransactionNumber%5Ealpha&searchOperator=%3D&dbSearchValue1={search_value}"
        st.driver.open(url)
        html = st.driver.page_source
        table = st.get_table(html, "ListOpportunitiesTable")
        links = st.get_table_links(table, 0)
        all_links.extend(links)

    for row in all_links:
        print(row)


download_missing_pages()
quit()


url = "https://ibs.stoneprofits.com/vQuote.aspx?ID=95233#tab=4"

# # save page
# st.open_connection()
# st.driver.open(url)
# # st.save_page_source("test_quote_no_wait.html")


# quit()

st.start_browser()

urls = [
    "https://www.cnn.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.amazon.com",
    "https://www.wikipedia.org",
]

for url in urls:
    st.driver.execute_script(f"window.open('{url}');")

# Iterate over each tab
for handle in st.driver.window_handles:
    print(handle)

    st.driver.switch_to.window(handle)
    if st.driver.current_url == "chrome://new-tab-page/":
        continue

    if st.driver.current_url == "about:blank":
        continue
    # Wait for the page to finish loading
    st.driver.wait_for_element_present("body")  # Adjust the selector as needed

    # Perform actions on the current tab
    # ...

    # Print a message and close the tab
    print(f"Done: {st.driver.current_url}")
    st.driver.close()

st.driver.execute_script("window.open('https://sjmulder.nl/en/textonly');")
st.driver.sleep(10)
quit()

thread_list = list()


def newtab(url):
    st.driver.execute_script("window.open('');")  # Opens a new tab
    new_tab = st.driver.window_handles[-1]  # Get the handle for the new tab
    st.driver.switch_to.window(new_tab)  # Switch to the new tab
    st.driver.get(url)


def do1():
    # Open new URL in a new tab
    # newtab()
    st.driver.get("http://cnn.com")
    st.driver.get("http://fox.com")


def do2():
    # newtab()
    st.driver.get("http://en.wikipedia.org")  # Open the new URL in the new tab
    st.driver.get("http://bbc.com")  # Open the new URL in the new tab


st.start_browser()
newtab("http://fox.com")
newtab("http://en.wikipedia.org")  # Open the new URL in the new tab
newtab("http://bbc.com")  # Open the new URL in the new tab)

exit()


t = threading.Thread(name="do2", target=do2)
t.start()
time.sleep(1)
print(t.name + " started!")
thread_list.append(t)


t = threading.Thread(name="do1", target=do1)
t.start()
time.sleep(1)
print(t.name + " started!")
thread_list.append(t)


# Wait for all threads to complete
for thread in thread_list:
    thread.join()


exit()

# l.st.driver.open("https://en.wikipedia.org/wiki/Banjul")


# # l.st.driver.open("https://en.wikipedia.org/wiki/Banjul")


# l.st.driver.execute_script("window.open('');")
# l.st.driver.open("https://en.wikipedia.org/")  # Opens a new tab

# quit()

# # # save page
# st.open_connection()
# st.driver.open(url)

# # # # Wait for the table to be present, with a timeout of 12 seconds
# try:
#     st.driver.wait_for_element_present("#filterfiletable", timeout=12)
# except Exception:
#     print("Table did not appear within 12 seconds. Continuing...")

# st.save_page_source("test_quote.html")

# quit()


# def extract_file_info(html_content):
#     soup = BeautifulSoup(html_content, "html.parser")
#     table = soup.find("table", {"id": "blah_filterfiletable"})

#     # filterfiletable
#     file_info = []

#     if table:
#         rows = table.find_all("tr")[1:]  # Skip the header row
#         for row in rows:
#             title_cell = row.find("td", {"class": "", "title": True})
#             if title_cell:
#                 title = title_cell.get("title")
#                 link = title_cell.find("a", href=True)
#                 if link:
#                     url = link.get("href")
#                     file_info.append({"title": title, "url": url})

#     return file_info


# filename = "test_quote.html"

# html_content = mymod.read_file(filename)

# result = extract_file_info(html_content)

# for item in result:
#     print(f"Title: {item['title']}")
#     print(f"URL: {item['url']}")
#     print()
