import scrape_html_pages as sh
import table_info as ti


def init_paths():
    sh.TOP_LEVEL_PAGE_FILE = "sipl_dsi/top_level_pages.json"
    sh.SUB_PAGES_DIRECTORY = "sipl_dsi/subpages/"
    sh.TABLE = ti.table_info["supplier_invoices"]


def download_subpages(start_num=0, end_num=None):
    init_paths()
    sh.start_browser()
    sh.save_linked_pages(start_num=start_num, end_num=end_num)


def download_top_pages():
    init_paths()
    sh.start_browser()
    sh.save_top_pages()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download linked pages.")
    parser.add_argument(
        "--start_num", type=int, default=0, help="Starting index for links"
    )
    parser.add_argument(
        "--end_num", type=int, default=None, help="Ending index for links (optional)"
    )
    args = parser.parse_args()

    download_subpages(start_num=args.start_num, end_num=args.end_num)
