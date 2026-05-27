import os #os USED FOR CREATING FOLDERS, CHECKING FILE PATH,RENAMING AND DELETING FILES
import json
import shutil
from datetime import datetime

from anyio.streams import file

DATA_FILE = "users.json"

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def pause():
    input("\nPress Enter to continue...")

#LOAD USER DATA FROM JSON FILE
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def get_user_folder(username):
    return "storage_" + username

def fix_user_data(users, username):
    if "files" not in users[username]:
        users[username]["files"] = []

    if "folders" not in users[username]:
        users[username]["folders"] = []

    if "shared_files" not in users[username]:
        users[username]["shared_files"] = []

    if "trash" not in users[username]:
        users[username]["trash"] = []

    user_folder = get_user_folder(username)
    os.makedirs(user_folder, exist_ok=True)
    os.makedirs(os.path.join(user_folder, "Shared"), exist_ok=True)
    os.makedirs(os.path.join(user_folder, "Trash"), exist_ok=True)

    save_users(users)

def register(users):
    username = input("Create username: ")
    if username in users:
        print("Username already exists.")
        return

    password = input("Create password: ")
    quota = float(input("Enter storage quota in MB: "))
    users[username] = {
        "password": password,
        "quota": quota,
        "used_storage": 0,
        "files": [],
        "folders": [],
        "shared_files": [],
        "trash": []
    }
    user_folder = get_user_folder(username)
    os.makedirs(user_folder, exist_ok=True)
    os.makedirs(os.path.join(user_folder, "Shared"), exist_ok=True)
    os.makedirs(os.path.join(user_folder, "Trash"), exist_ok=True)
    save_users(users)
    print("Account created successfully.")

#LOGIN
def login(users):
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in users and users[username]["password"] == password:
        fix_user_data(users, username)
        print("Login successful.")
        return username

    print("Invalid username or password.")
    return None

#FOLDER CREATION
def create_folder(users, username):
    folder_name = input("Enter folder name: ")
    path = os.path.join(get_user_folder(username), folder_name)
    if os.path.exists(path):
        print("Folder already exists.")
        return

    os.mkdir(path)
    users[username]["folders"].append(folder_name)
    save_users(users)
    print("Folder created successfully.")

#SHOWING THE FOLDER
def show_folders(users, username):
    folders = users[username]["folders"]
    if len(folders) == 0:
        print("No folders created.")
        return

    print("\nFolders:")
    for folder in folders:
        print("-", folder)

#UPLOAD THE FILE
def upload_file(users, username):
    source_path = input("Enter full file path: ")
    if not os.path.exists(source_path):
        print("File does not exist.")
        return
    file_name = os.path.basename(source_path)
    file_size = os.path.getsize(source_path) / (1024 * 1024)

    user = users[username]
    if user["used_storage"] + file_size > user["quota"]:
        print("Upload failed. Storage quota exceeded.")
        return

    print("\nWhere do you want to upload?")
    print("1. Main storage")
    print("2. Inside a folder")

    choice = input("Enter choice: ")
    folder_name = "Main"
    if choice == "2":
        show_folders(users, username)
        folder_name = input("Enter folder name: ")
        folder_path = os.path.join(get_user_folder(username), folder_name)

        if not os.path.exists(folder_path):
            print("Folder does not exist.")
            return

        destination = os.path.join(folder_path, file_name)
    else:
        destination = os.path.join(get_user_folder(username), file_name)

    shutil.copy(source_path, destination)
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["files"].append({
        "name": file_name,
        "size": round(file_size, 2),
        "folder": folder_name,
        "uploaded_at": upload_time
    })

    user["used_storage"] += file_size
    save_users(users)
    print("File uploaded successfully.")
    print("Uploaded at:", upload_time)

#SHOW FOLDER
def show_files(users, username):
    files = users[username]["files"]

    if len(files) == 0:
        print("No files uploaded.")
        return

    print("\nFiles:")

    for file_info in files:
        uploaded_time = file_info.get("uploaded_at", "Old File")
        folder_name = file_info.get("folder", "Main")

        print(
            file_info["name"],
            "-",
            file_info["size"],
            "MB",
            "- Folder:",
            folder_name,
            "- Uploaded:",
            uploaded_time
        )

def search_file(users, username):
    keyword = input("Enter search keyword: ")
    found = False
    print("\nSearch Results:")
    for file_info in users[username]["files"]:
        if keyword.lower() in file_info["name"].lower():
            uploaded_time = file_info.get("uploaded_at", "Old File")
            folder_name = file_info.get("folder", "Main")

            print(
                file_info["name"],
                "-",
                file_info["size"],
                "MB",
                "- Folder:",
                folder_name,
                "- Uploaded:",
                uploaded_time
            )
            found = True
    if not found:
        print("No matching files found.")


def get_file_path(username, file):
    if file["folder"] == "Main":
        return os.path.join(get_user_folder(username), file["name"])
    else:
        return os.path.join(get_user_folder(username), file["folder"], file["name"])

#MOVE DELETED FILE IN TRASH FOLDER
def delete_file(users, username):
    file_name = input("Enter file name to move to trash: ")

    files = users[username]["files"]

    for file in files:
        if file["name"] == file_name:
            old_path = get_file_path(username, file)

            trash_folder = os.path.join(get_user_folder(username), "Trash")
            os.makedirs(trash_folder, exist_ok=True)
            new_path = os.path.join(trash_folder, file_name)

            if os.path.exists(old_path):
                shutil.move(old_path, new_path)

            file["deleted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            users[username]["trash"].append(file)
            files.remove(file)
            save_users(users)
            print("File moved to trash successfully.")
            return

    print("File not found.")


def show_trash(users, username):
    trash = users[username]["trash"]
    if len(trash) == 0:
        print("Trash is empty.")
        return
    print("\nTrash Bin:")
    for file in trash:
        print(
            file["name"],
            "-",
            file["size"],
            "MB",
            "- Deleted:",
            file["deleted_at"]
        )


def restore_file(users, username):
    file_name = input("Enter file name to restore: ")
    trash = users[username]["trash"]
    for file in trash:
        if file["name"] == file_name:
            trash_path = os.path.join(get_user_folder(username), "Trash", file_name)

            if file["folder"] == "Main":
                restore_path = os.path.join(get_user_folder(username), file_name)
            else:
                folder_path = os.path.join(get_user_folder(username), file["folder"])
                os.makedirs(folder_path, exist_ok=True)
                restore_path = os.path.join(folder_path, file_name)

            if os.path.exists(trash_path):
                shutil.move(trash_path, restore_path)

            if "deleted_at" in file:
                del file["deleted_at"]

            users[username]["files"].append(file)
            trash.remove(file)
            save_users(users)
            print("File restored successfully.")
            return
    print("File not found in trash.")


def permanently_delete_file(users, username):
    file_name = input("Enter file name to permanently delete: ")
    trash = users[username]["trash"]
    for file in trash:
        if file["name"] == file_name:
            trash_path = os.path.join(get_user_folder(username), "Trash", file_name)

            if os.path.exists(trash_path):
                os.remove(trash_path)

            users[username]["used_storage"] -= file["size"]
            trash.remove(file)
            save_users(users)
            print("File permanently deleted.")
            return
    print("File not found in trash.")


def rename_file(users, username):
    old_name = input("Enter current file name: ")
    new_name = input("Enter new file name: ")

    # Check empty name
    if new_name.strip() == "":
        print("New file name cannot be empty.")
        return

    files = users[username]["files"]

    for file_info in files:

        if file_info["name"] == old_name:

            old_path = get_file_path(username, file_info)

            # Keep same folder
            if file_info.get("folder", "Main") == "Main":
                new_path = os.path.join(
                    get_user_folder(username),
                    new_name
                )
            else:
                new_path = os.path.join(
                    get_user_folder(username),
                    file_info["folder"],
                    new_name
                )

            # Prevent duplicate filename
            if os.path.exists(new_path):
                print("A file with that name already exists.")
                return

            # Rename real file
            os.rename(old_path, new_path)

            # Update JSON data
            file_info["name"] = new_name
            save_users(users)
            print("File renamed successfully.")
            return

    print("File not found.")


def download_file(users, username):
    file_name = input("Enter file name to download: ")
    download_path = input("Enter destination folder path: ")

    if not os.path.exists(download_path):
        print("Destination folder does not exist.")
        return

    for file in users[username]["files"]:
        if file["name"] == file_name:
            source_path = get_file_path(username, file)
            destination = os.path.join(download_path, file_name)

            if os.path.exists(source_path):
                shutil.copy(source_path, destination)
                print("File downloaded successfully.")
                return

    print("File not found.")


def storage_info(users, username):
    user = users[username]
    remaining = user["quota"] - user["used_storage"]
    print("\nStorage Information")
    print("Total Quota:", user["quota"], "MB")
    print("Used Storage:", round(user["used_storage"], 2), "MB")
    print("Remaining Storage:", round(remaining, 2), "MB")

#SHARE FILE WITH ANOTHER REGISTERED USER
def share_file(users, username):
    file_name = input("Enter file name to share: ")
    receiver = input("Enter receiver username: ")

    if receiver not in users:
        print("Receiver does not exist.")
        return

    if receiver == username:
        print("You cannot share a file with yourself.")
        return

    if "shared_files" not in users[receiver]:
        users[receiver]["shared_files"] = []

    for file_info in users[username]["files"]:
        if file_info["name"] == file_name:
            source_path = get_file_path(username, file_info)
            if not os.path.exists(source_path):
                print("File not found in storage folder.")
                return

            shared_folder = os.path.join(get_user_folder(receiver), "Shared")
            os.makedirs(shared_folder, exist_ok=True)
            destination = os.path.join(shared_folder, file_name)
            shutil.copy(source_path, destination)
            users[receiver]["shared_files"].append({
                "name": file_name,
                "from": username,
                "shared_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            save_users(users)
            print("File shared successfully.")
            return

    print("File not found.")

def view_shared_files(users, username):
    if "shared_files" not in users[username]:
        users[username]["shared_files"] = []
        save_users(users)

    shared_files = users[username]["shared_files"]
    if len(shared_files) == 0:
        print("No shared files.")
        return

    print("\nShared Files:")
    for file_info in shared_files:
        print(
            file_info["name"],
            "- Shared by:",
            file_info["from"],
            "- Shared at:",
            file_info.get("shared_at", "Unknown")
        )

def user_menu(users, username):
    while True:
        clear_screen()
        print("--- User Menu ---")
        print("Logged in as:", username)
        print("1. Upload File")
        print("2. Delete File")
        print("3. Rename File")
        print("4. Search File")
        print("5. Show All Files")
        print("6. View Storage")
        print("7. Create Folder")
        print("8. Show Folders")
        print("9. Share File")
        print("10. View Shared Files")
        print("11. Download File")
        print("12. Show Trash")
        print("13. Restore File")
        print("14. Permanently Delete File")
        print("15. Logout")
        choice = input("Enter choice: ")
        clear_screen()

        if choice == "1":
            upload_file(users, username)
            pause()
        elif choice == "2":
            delete_file(users, username)
            pause()
        elif choice == "3":
            rename_file(users, username)
            pause()
        elif choice == "4":
            search_file(users, username)
            pause()
        elif choice == "5":
            show_files(users, username)
            pause()
        elif choice == "6":
            storage_info(users, username)
            pause()
        elif choice == "7":
            create_folder(users, username)
            pause()
        elif choice == "8":
            show_folders(users, username)
            pause()
        elif choice == "9":
            share_file(users, username)
            pause()
        elif choice == "10":
            view_shared_files(users, username)
            pause()
        elif choice == "11":
            download_file(users, username)
            pause()
        elif choice == "12":
            show_trash(users, username)
            pause()
        elif choice == "13":
            restore_file(users, username)
            pause()
        elif choice == "14":
            permanently_delete_file(users, username)
            pause()
        elif choice == "15":
            print("Logged out.")
            pause()
            break
        else:
            print("Invalid choice.")
            pause()

def main():
    users = load_users()
    while True:
        clear_screen()
        print("=== Mini Cloud Storage Simulator ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")
        clear_screen()
        if choice == "1":
            register(users)
            pause()
        elif choice == "2":
            current_user = login(users)
            pause()
            if current_user:
                user_menu(users, current_user)
        elif choice == "3":
            print("Program closed.")
            break
        else:
            print("Invalid choice.")
            pause()

main()
