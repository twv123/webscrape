""" Scrape data from StoneProfits website. """

import argparse
import file_download as fd


def do_choice(choice, args):
    """Execute code based on choice."""
    if choice == 1:
        fd.start_browser()
        fd.save_top_pages()
    elif choice == 2:
        fd.start_browser()
        fd.get_child_html_pages(start_num=args.start_num, end_num=args.end_num)
    elif choice == 3:
        fd.start_browser()
        fd.get_child_html_pages(True, start_num=args.start_num, end_num=args.end_num)
    elif choice == 4:
        fd.start_browser()
        fd.process_file_downloads(
            args.file_dl_key, start_num=args.start_num, end_num=args.end_num
        )
    elif choice == 5:
        fd.CONFIG.use_download_links_csv = True
        fd.start_browser()
        fd.process_file_downloads(
            args.file_dl_key, start_num=args.start_num, end_num=args.end_num
        )
    elif choice == 6:
        fd.start_browser()
        fd.save_top_pages()
        fd.get_child_html_pages(start_num=args.start_num, end_num=args.end_num)
        fd.process_file_downloads(args.file_dl_key)
    elif choice == 7:
        fd.get_sub_page_links()
    elif choice == 8:
        fd.set_debug_flag(not fd.get_debug_flag())
    elif choice == 9:
        quit()
    elif choice == 10:
        fd.check_file_quality()
    elif choice == 11:
        fd.print_missing_files()
    elif choice == 12:
        fd.start_browser()
        fd.CONFIG.use_download_links_csv = True
        fd.try_downloading_missed_files()
    elif choice == 13:
        fd.get_all_download_links()
    elif choice == 14:
        fd.get_product_images()
    elif choice == 15:
        fd.get_product_images(True)
    elif choice == 16:
        fd.quality_check_products()
    elif choice == 17:
        fd.download_missing_images()
    else:
        print("Invalid choice. Please enter a number between 1 and 15.")
    return


def get_choice():
    """Prints options, and gets user selection."""
    print("\n-------------------------")
    print("Choose run option:")
    print("  1. Save top level pages.")
    print("  2. Save child pages (files tables).")
    print("  3. Save child pages (files tables) - use links.csv.")
    print("  4. Download files.(use --file_dl_key for specific key)")
    print("  5. Download files.(use --file_dl_key for specific key)- use dl_links.csv")
    print("  6. *** Run full process.")
    print("\n  ----------")
    print("  7. Create links.csv (and secondary_links.csv) file from top level pages.")
    print("  8. Toggle debug flag.")
    print("  9. Quit.")
    print("\n  ---- Quality and missing files.")
    print("  10. Quality check. (Missing download files)")
    print("  11. Print missing download files from 'missing.csv'.")
    print("  12. Download missing files. (Uses dl_links.csv)")
    print("  13. Get download links - create 'dl_links.csv'.")
    print("\n  ---- Product Images")
    print("  14. Get product images.")
    print("  15. Get product images. (read from link file)")
    print("  16. Quality check product images.")
    print("  17. Download missing images.")

    return int(input("Enter your choice (1-11): "))


def do_session(args):
    """Initializes the DownloadConfig class and starts the download processes."""
    print(f"args: {args}")
    if args.table_config == "":
        args.table_config = input("A Table config name is required: ")

    print(f"Getting config for table: {args.table_config}")
    fd.set_table_config(args.table_config)
    fd.set_debug_flag(args.debug)
    fd.CONFIG.set_logon_id(args.logon_id)

    if args.option is not None:
        do_choice(args.option, args)

    while True:
        do_choice(get_choice(), args)


def main():
    """Main handler for downloading files"""
    parser = argparse.ArgumentParser(description="Download linked pages.")
    parser.add_argument(
        "--start_num", type=int, default=0, help="Starting index for links. (optional)"
    )
    parser.add_argument(
        "--end_num", type=int, default=None, help="Ending index for links. (optional)"
    )
    parser.add_argument(
        "--option",
        type=int,
        choices=list(range(1, 18)),
        help="Specify an option (1, 2, or 3).",
    )
    parser.add_argument(
        "--logon_id",
        type=int,
        default=0,
        help="Specify the logon ID. (0 = IBS, 1 = DSI",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument(
        "--table_config", type=str, default="", help="Specify the table configuration."
    )
    parser.add_argument(
        "--file_dl_key", type=str, default="", help="Specify the key to download."
    )
    args = parser.parse_args()
    do_session(args)


if __name__ == "__main__":
    main()

    # filename = "downloads/opps/opp_link_refs.csv"
    # links = mymod.read_csv_file(filename)
    # print(links[:20])
    # new_links = mymod.remove_array_dups(links)
    # mymod.write_data_to_csv(new_links, filename, True, "w")
