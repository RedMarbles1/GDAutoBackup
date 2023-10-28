import subprocess
import json
import argparse
from pydrive2.drive import GoogleDrive
from pydrive2.auth import GoogleAuth
import os

# Initialize Google Drive
gauth = GoogleAuth()
gauth.LoadCredentialsFile("gdrivecreds.txt")  # Load credentials from a file
if gauth.credentials is None:
    # Authenticate if credentials do not exist
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("gdrivecreds.txt")  # Save credentials to a file
drive = GoogleDrive(gauth)

# Helper function to resolve or create folders
def resolve_or_create_folder(parent_id, folder_name):
    folder_list = drive.ListFile({
        'q': f"'{parent_id}' in parents and title='{folder_name}' and trashed=false and mimeType='application/vnd.google-apps.folder'",
        'fields': 'items(id, title)',
    }).GetList()

    if folder_list:
        return folder_list[0]['id']
    else:
        folder = drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_id}]
        })
        folder.Upload()
        return folder['id']

# Function to resolve or create the main folder
def resolve_or_create_main_folder():
    mainfolder_id = resolve_or_create_folder('root', 'GDAutoBackup')
    return mainfolder_id

# Function to restore backups from Google Drive to the save path
def restore_backup(appname, mainfolder_id):
    folder_id = resolve_or_create_folder(mainfolder_id, appname)
    folder_content = drive.ListFile({'q': f"'{folder_id}' in parents"}).GetList()

    for file in folder_content:
        file.GetContentFile(os.path.join(savepath, file['title']))

# Function to update the JSON configuration interactively
def update_config(config):
    while True:
        print("\nCurrent Configuration:")
        for appname, app_info in config.items():
            print(f"App: {appname}")
            print(f"Path: {app_info['path']}")
            print(f"Save Path: {app_info.get('savepath', '')}")
            print()

        action = input("Select an action (add/edit/remove/quit): ").lower()

        if action == "add":
            appname = input("Enter the app name: ")
            path = input("Enter the app path: ").replace("\\", "/")
            savepath = input("Enter the save path (optional): ").replace("\\", "/")
            config[appname] = {"path": path}
            if savepath:
                config[appname]["savepath"] = savepath

        elif action == "edit":
            appname = input("Enter the app name to edit: ")
            if appname in config:
                app_info = config[appname]
                path = input(f"Enter the new app path for {appname} (or keep it same if empty): ").replace("\\", "/")
                if path:
                    app_info["path"] = path
                savepath = input(f"Enter the new save path for {appname} (or keep it same if empty): ").replace("\\", "/")
                if savepath:
                    app_info["savepath"] = savepath
            else:
                print(f"App '{appname}' not found in the configuration.")

        elif action == "remove":
            appname = input("Enter the app name to remove: ")
            if appname in config:
                del config[appname]
                print(f"Removed app '{appname}' from the configuration.")
            else:
                print(f"App '{appname}' not found in the configuration.")

        elif action == "quit":
            break

        else:
            print("Invalid action. Please enter 'add', 'edit', 'remove', or 'quit'.")

        with open("apps.json", "w") as json_file:
            json.dump(config, json_file, indent=4)

# Parse command-line arguments
parser = argparse.ArgumentParser(
    prog="GDAutoBackup",
    description="Automatically backs up folders of an app when the app is closed, and restores it back on the next launch."
)
parser.add_argument("-l", "--launch", dest="launch", metavar="AppName", help="Specify app name to launch. The app and its paths must be added to apps.json beforehand. Launch the program with no arguments to go into editor mode and add a new app.")
args = parser.parse_args()

# Load app information from a JSON file
with open("apps.json", "r") as openfile:
    appjson = json.load(openfile)

# Interactive configuration update if no launch argument is provided
if not args.launch:
    update_config(appjson)

if args.launch:
    appname = args.launch
    if appname in appjson:
        app_info = appjson[appname]
        app_path = app_info["path"]
        savepath = app_info.get("savepath", "")

        # Resolve or create the main folder
        mainfolder_id = resolve_or_create_main_folder()

        # Restore backups from Google Drive to the save path
        print(f"Restoring data...")
        restore_backup(appname, mainfolder_id)

        print(f"Opening {appname}...")
        app = subprocess.Popen(app_path)
        print(f"Waiting for {appname} to close...")
        app.wait()
        print(f"{appname} Closed. Starting backup process...")

        folder_id = resolve_or_create_folder(mainfolder_id, appname)

        # Clear existing contents in the subfolder
        print(f"Clearing old files on Google Drive...")
        existing_files = drive.ListFile({'q': f"'{folder_id}' in parents"}).GetList()
        for file in existing_files:
            file.Delete()
        print(f"Clearing up done. Starting new backup...")
        # Backup the specified folder to Google Drive
        for x in os.listdir(savepath):
            file_path = os.path.join(savepath, x)
            if os.path.isfile(file_path):
                f = drive.CreateFile({
                    'title': x,
                    'parents': [{'id': folder_id}]
                })
                f.SetContentFile(file_path)
                f.Upload()
            elif os.path.isdir(file_path):
                print(f"Skipping directory: {x}")

        print(f"Backup for {appname} Completed.")
    else:
        print(f"App '{appname}' not found in the JSON file.")

print("Process Completed.")
SystemExit