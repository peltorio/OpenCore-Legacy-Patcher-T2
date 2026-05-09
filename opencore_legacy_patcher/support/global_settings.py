"""
global_settings.py: Library for querying and writing global enviroment settings

Alternative to Apple's 'defaults' tool
Store data in '/Users/Shared'
This is to ensure compatibility when running without a user
ie. during automated patching
"""

import logging
import plistlib
import os

from pathlib import Path

# Check if the file is owned by the current user or root
file_info = os.stat(self.global_settings_plist)
if file_info.st_uid not in [0, os.getuid()]:
    raise PermissionError("Security Error: Settings file is owned by an untrusted user.")

class GlobalEnviromentSettings:
    """
    Library for querying and writing global enviroment settings
    """

    def __init__(self) -> None:
        self.file_name:              str = ".com.dortania.opencore-legacy-patcher.plist"
        self.global_settings_folder: str = "/Users/Shared"
        self.global_settings_plist:  str = f"{self.global_settings_folder}/{self.file_name}"

        self._generate_settings_file()
        self._convert_defaults_to_global_settings()


    def read_property(self, property_name: str) -> str:
        """
        Reads a property from the global settings file
        """
        # Security: Don't read from a symlink
        if Path(self.global_settings_plist).is_symlink():
            return None

        if Path(self.global_settings_plist).exists():
            try:
                plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            except Exception as e:
                logging.error("Error: Unable to read global settings file")
                logging.error(e)
                return None
            if property_name in plist:
                return plist[property_name]
        return None

    def delete_property(self, property_name: str) -> None:
        """
        Deletes a property from the global settings file
        """
        if Path(self.global_settings_plist).exists():
            try:
                plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            except Exception as e:
                logging.error("Error: Unable to read global settings file")
                logging.error(e)
                return
            if property_name in plist:
                del plist[property_name]
                try:
                    plistlib.dump(plist, Path(self.global_settings_plist).open("wb"))
                except PermissionError:
                    logging.info("Failed to write to global settings")


    def write_property(self, property_name: str, property_value) -> None:
        """
        Writes a property to the global settings file
        """
        # FIX: Added Symlink Protection
        if Path(self.global_settings_plist).is_symlink():
            logging.warning("Security Alert: Symlink detected at settings path. Deleting for safety.")
            Path(self.global_settings_plist).unlink()

        if Path(self.global_settings_plist).exists():
            try:
                plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            except Exception as e:
                logging.error("Error: Unable to read global settings file")
                logging.error(e)
                return
            
            plist[property_name] = property_value
            try:
                plistlib.dump(plist, Path(self.global_settings_plist).open("wb"))
            except PermissionError:
                logging.info("Failed to write to global settings file")
    def _generate_settings_file(self) -> None:
        # FIX: Added Symlink Protection
        if Path(self.global_settings_plist).is_symlink():
            logging.warning("Security Alert: Symlink detected at settings path. Deleting for safety.")
            Path(self.global_settings_plist).unlink()

        if Path(self.global_settings_plist).exists():
            return
            
        try:
            # Ensure directory exists
            Path(self.global_settings_folder).mkdir(parents=True, exist_ok=True)
            plistlib.dump({"Developed by Dortania": True,}, Path(self.global_settings_plist).open("wb"))
        except PermissionError:
            logging.info("Permission error: Unable to write to global settings file")

    # ... remaining methods (delete_property, _convert_defaults_to_global_settings) ...    

    def _convert_defaults_to_global_settings(self) -> None:
        """
        Converts legacy defaults to global settings
        """

        defaults_path = "~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist"
        defaults_path = Path(defaults_path).expanduser()

        if Path(defaults_path).exists():
            # merge defaults with global settings
            try:
                defaults_plist = plistlib.load(Path(defaults_path).open("rb"))
                global_settings_plist = plistlib.load(Path(self.global_settings_plist).open("rb"))
            except Exception as e:
                logging.error("Error: Unable to read global settings file")
                logging.error(e)
                return
            global_settings_plist.update(defaults_plist)
            try:
                plistlib.dump(global_settings_plist, Path(self.global_settings_plist).open("wb"))
            except PermissionError:
                logging.info("Permission error: Unable to write to global settings file")
                return

            # delete defaults plist
            try:
                Path(defaults_path).unlink()
            except Exception as e:
                logging.error("Error: Unable to delete defaults plist")
                logging.error(e)
