"""For debugging command line."""

import subprocess


# Define the command with arguments
command = [
    "python3",
    "file_download_main.py",
    "--table_config",
    "supplier_invoices",
    "--logon_id",
    "1"
    # "--debug",
    # "--option",
    # "5",
    # "--start_num",
    # "593",
    # "--end_num",
    # "598",
    # "--file_dl_key",
    # "11237B",
]

# Run the command without capturing output
subprocess.run(command, check=True)
