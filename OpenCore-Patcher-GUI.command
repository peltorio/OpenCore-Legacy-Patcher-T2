#!/usr/bin/env python3
"""
PyInstaller Entry Point - Hardened
"""
import sys
import logging
import os
import zipfile
import shutil
from pathlib import Path

# SECURITY FIX: Remove the current directory from the search path.
if "" in sys.path:
    sys.path.remove("")

# We configure logging to write to sys.stdout (the Terminal window)
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s', # Keep it clean for the Terminal
    stream=sys.stdout
)

def extract_and_copy_tools():
    """
    Finds OpenCoreLegacyPatcherTools.zip and extracts ocvalidate and macserial 
    to payloads > OpenCore.
    """
    try:
        # Determine the base directory where the script/app is running
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parent

        # 1. Find the Tools Zip file (Look for any zip containing 'Tools' in the name)
        zip_path = None
        for file in base_dir.rglob("*Tools*.zip"):
            zip_path = file
            break

        if not zip_path:
            # Fallback check if it's in a T2 specific folder nearby
            for file in base_dir.rglob("**/OpenCore-Legacy-Patcher-T2/**/*.zip"):
                zip_path = file
                break

        if not zip_path:
            print("[WARN] OpenCoreLegacyPatcherTools.zip not found. Proceeding without extraction.")
            return

        print(f"[INFO] Found tools at: {zip_path}")

        # 2. Define the destination path: payloads/OpenCore
        dest_dir = base_dir / "payloads" / "OpenCore"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # 3. Extract necessary files
        print("[INFO] Extracting tools...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Iterate through files in the zip to find the ones we want
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(('ocvalidate', 'macserial')):
                    
                    # Extract to a temporary directory inside the payload folder or straight to destination
                    extracted_path = zip_ref.extract(file_info, path=dest_dir)
                    
                    # If it extracted inside a nested folder structure within the zip, move it to root payloads/OpenCore
                    target_file_path = dest_dir / os.path.basename(file_info.filename)
                    if extracted_path != str(target_file_path):
                        shutil.move(extracted_path, target_file_path)
                        
                    print(f"  > Copied: {os.path.basename(file_info.filename)}")

        print("[INFO] Tools successfully extracted to payloads/OpenCore.\n")

    except Exception as e:
        print(f"[ERROR] Failed to extract tools: {e}")


from opencore_legacy_patcher import main

if __name__ == '__main__':
    try:
        # Run the extraction process before starting the main Patcher application
        extract_and_copy_tools()
        
        # Normal launch attempt
        main()
    except Exception as e:
        # THIS ONLY PRINTS TO TERMINAL IF THE APP FAILS
        print("\n" + "="*60)
        
        # 1. human-friendly error
        logging.error("Whoops, the app crashed because of the following error:")
        print(f"Direct Error: {e}")
        
        print("-" * 60)
        
        # 2. This prints the full technical log (Stack Trace) to the Terminal
        logging.exception("Stack Trace:")
        
        print("="*60)
        
        # 3. Keep the Terminal window open so the tester can copy the text
        input("\nPress ENTER to close this window...")
        sys.exit(3)
