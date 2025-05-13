"""Check for missing downloads."""

import os
import modules.my_common_module as mymod


class QualityCheck:
    """Check for missing or misplaced downloaded files."""

    def __init__(self, directory_path):
        self.directory_path = directory_path
        if self.directory_path.endswith("files/"):
            self.top_level_path = self.directory_path[: -len("files/")]
        else:
            self.top_level_path = self.directory_path

        self.access_denied_files = []
        access_denied_file = self.top_level_path + "access_denied_files.csv"
        if mymod.is_file_exists(access_denied_file):
            print("Reading access_denied_file.")
            self.access_denied_files = mymod.read_csv_file(access_denied_file)

    def __is_access_denied_file(self, key, filename):
        # if not self.access_denied_files:
        #     return False
        for file in self.access_denied_files:
            if file[0].lower() == key.lower() and file[1].lower() == filename.lower():
                return True
        return False

    def missing_files(self, key_filename_array):
        """Get list of files not downloaded."""
        missing_files = []
        counter = 0
        qty = len(key_filename_array)
        for key, filename, url in key_filename_array:
            counter += 1
            print(f"Checking key {counter}/{qty}...", end="\r")

            if self.__is_access_denied_file(key, filename):
                continue
            file_path = os.path.join(self.directory_path, key, filename)
            file_path = file_path.replace("//", "/")
            if not os.path.exists(file_path):
                # Check if a case-insensitive match exists
                for existing_file in os.listdir(os.path.join(self.directory_path, key)):
                    if existing_file.lower() == filename.lower():
                        break
                else:
                    missing_files.append([key, filename, url])

        # Save the csv to the top level for the table.  (Drop the 'files/')

        if self.directory_path.endswith("files/"):
            path = self.directory_path[: -len("files/")]
        else:
            path = self.directory_path

        csv_filename = path + "missing_files.csv"
        mymod.write_data_to_csv(missing_files, csv_filename, mode="w")
        return missing_files  # , extra_files
