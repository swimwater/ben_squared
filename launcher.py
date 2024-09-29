import subprocess
import sys
import os
from pathlib import Path
import argparse

def find_script(script_name, search_directory='.'):
    """
    Search for the script in subdirectories.
    :param script_name: The name of the script to search for (e.g., 'Script.py').
    :param search_directory: The root directory to start the search.
    :return: Full path to the script if found, else None.
    """
    # Traverse the directory and subdirectories
    for root, dirs, files in os.walk(search_directory):
        if script_name in files:
            return Path(root) / script_name
    return None

def launch_detached(script_path, show_console=False):
    creation_flags = 0
    if not show_console:
        creation_flags = subprocess.CREATE_NO_WINDOW  # Hide console
    else:
        creation_flags = subprocess.CREATE_NEW_CONSOLE  # Show console

    # Launch the specified script
    subprocess.Popen([sys.executable, script_path], creationflags=creation_flags)

if __name__ == "__main__":
    # Argument parser to handle script selection and console visibility
    parser = argparse.ArgumentParser(description="Launch a Python script in detached mode.")
    parser.add_argument('script_name', type=str, help="The Python script to launch (e.g., Script.py)")
    parser.add_argument('--show-console', action='store_true', help="Show the console window")

    # Parse the arguments
    args = parser.parse_args()

    # Search for the script in the current directory and subdirectories
    script_path = find_script(args.script_name)

    if script_path:
        # Launch the script if found
        launch_detached(script_path, show_console=args.show_console)
        print(f"Launching {script_path}...")
    else:
        print(f"Error: {args.script_name} not found in subdirectories.")
