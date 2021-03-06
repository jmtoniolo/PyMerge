"""
###########################################################################
File: file_backup.py
Author:
Description: Module for creating file backups before file merges are saved.


Copyright (C) PyMerge Team 2019

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################
"""

import hashlib
import os
import pickle
import pathlib
import zipfile


class Backup(object):
    __slots__ = ["BLOCK_SIZE", "hash_type", "hash_func"]

    def __init__(self, hash_type="SHA256", block_size=65535):
        """
        Initialize the Backup class
        :param hash_type: Type of hash function to use. Defaults to SHA256
        :param block_size: Size of block to be read from file when calculating hash
        """
        self.BLOCK_SIZE: int = block_size
        self.hash_type: str = hash_type
        self.hash_func = hashlib.sha256  # Default to SHA256
        self.hash_func = self.get_hash_func(hash_type)

    @staticmethod
    def get_hash_func(hash_type):
        # Choose the correct hash function
        if hash_type == "SHA224":
            return hashlib.sha224
        if hash_type == "SHA256":
            return hashlib.sha256
        if hash_type == "SHA512":
            return hashlib.sha512
        if hash_type == "MD5":
            return hashlib.md5
        else:
            return hashlib.sha256

    @staticmethod
    def format_datetime(date_time) -> str:
        """
        Format datetime as string with ':' and ' ' removed.
        :return: string containing datetime values
        """
        datetime_str = str(date_time)
        datetime_str = (
            datetime_str.replace(":", "")
            .replace(" ", "_")
            .replace("-", "")
            .replace(".", "")
        )
        return datetime_str

    @staticmethod
    def check_for_backup_folder():
        """
        Checks if the folder 'backup' exists and creates it if it doesn't.
        """
        if not os.path.exists("backup"):
            os.mkdir("backup")
        else:
            pass

    @staticmethod
    def get_meta_file_name(file_name: str) -> str:
        """
        Create the file name for the backup meta file.
        """
        return f".meta.{pathlib.Path(file_name).name}.dat"

    def create_meta_file(self, file: str) -> str:
        """
        Create a metadata file for use as comparison against unarchived file data
        :param file: file to be archived
        :return: string containing absolute path to metadata file
        """
        file_name = file.replace("\\", "/").split("/")[-1]
        meta_file_name = self.get_meta_file_name(file)
        meta_info: dict = {
            "NAME": file_name,
            "SIZE": int(os.stat(file).st_size),
            "MODIFIED": os.stat(file).st_mtime,
            "HASH_TYPE": self.hash_type,
        }

        with open(meta_file_name, "wb") as meta_file:
            pickle.dump({"META": meta_info}, meta_file)

        return os.path.abspath(meta_file_name)

    def get_hash(self, file: str) -> hex:
        """
        Calculates the hash value for a file
        :param file: file to get hash for
        :return: hex digest version of hash
        """
        with open(file, "rb") as in_file:
            file_buf = in_file.read(self.BLOCK_SIZE)
            # hash_obj = self.hash_func().update(file_buf)
            while len(file_buf) > 0:
                self.hash_func().update(file_buf)
                file_buf = in_file.read(self.BLOCK_SIZE)
        return self.hash_func().hexdigest()

    def check_hash(self, file, hash_value: str) -> bool:
        """
        Checks the validity of a hash value against the calculates hash for a file
        :param file:
        :param hash_value:
        :return: boolean indicating file integrity
        """
        return str(hash_value) == str(self.get_hash(file))

    @staticmethod
    def get_hash_file_name(hash_type: str) -> str:
        """
        Create the name for the backup hash file.
        """
        return f"{hash_type}.txt"

    def create_backup(self, file: str, backup_dir: str) -> str:
        """
        Creates a zip archive containing a backup of a file and the hash value

        :param file: file to be backed up
        :param backup_dir:
        :return: absolute path to backup
        """
        # Create hash file to use for integrity checks during backup retrieval
        hash_file = self.get_hash_file_name(self.hash_type)

        # Create meta data file to use as comparison when backup is retrieved
        meta_file = self.create_meta_file(file)

        with open(hash_file, "w+") as temp:
            temp.write(str(self.get_hash(file)))

        # Zip the files together
        with zipfile.ZipFile(
            f"{backup_dir}/{pathlib.Path(file).name}.bak", "w", zipfile.ZIP_DEFLATED
        ) as backup:
            backup.write(file)
            backup.write(hash_file)
            backup.write(meta_file)

        try:
            # Remove the created hash and meta data files after they are archived
            os.remove(hash_file)
            os.remove(meta_file)
        except FileNotFoundError:
            pass
        return os.path.abspath(f"{file}.bak")

    def retrieve_backup(self, backup_file, file_name):
        """
        Function to retrieve the backup file from the zip archive. Checks the hash value for integrity
        :param backup_file: backup file to extract
        :param file_name: file to be backed up
        :return: No return value
        """

        # Extract the archive contents
        with zipfile.ZipFile(backup_file) as myzip:
            myzip.extract(file_name)
            myzip.extract(f"{self.hash_type}.txt")
            myzip.extract(f".meta.{file_name}.dat")

        # Read the hash file contents
        with open(f"{self.hash_type}.txt", "r") as hash_file:
            hash_string = hash_file.read().strip("\n")

        # Check the integrity of the file against the included hash
        if not self.check_hash(backup_file.strip(".bak"), hash_string):
            os.remove(file_name)

        # Remove unecessary archive files
        os.remove(f"{self.hash_type}.txt")
        os.remove(f".meta.{file_name}.dat")

    def get_hash_from_backup(self, backup_file: str) -> str:
        """
        Gets the hash value from the text file stored in the backup archive.
        """
        # Extract the archive contents
        with zipfile.ZipFile(backup_file) as myzip:
            myzip.extract(f"{self.hash_type}.txt")

        # Read the hash file contents
        with open(f"{self.hash_type}.txt", "r") as hash_file:
            hash_string = hash_file.read().strip("\n")

        os.remove(f"{self.hash_type}.txt")
        return hash_string
