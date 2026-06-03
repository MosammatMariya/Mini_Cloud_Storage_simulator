import os
import json
import shutil
import hashlib
from datetime import datetime

DATA_FILE = "users.json"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_user_folder(username):
    return "storage_" + username

def detect_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif"]:
        return "Image"
    elif ext in [".pdf"]:
        return "PDF"
    elif ext in [".doc", ".docx"]:
        return "Word Document"
    elif ext in [".mp4", ".mov", ".avi"]:
        return "Video"
    elif ext in [".mp3", ".wav"]:
        return "Audio"
    elif ext in [".txt"]:
        return "Text File"
    else:
        return "Other"

def fix_user_data(users, username):
    user = users[username]
    user.setdefault("files", [])
    user.setdefault("folders", [])
    user.setdefault("shared_files", [])
    user.setdefault("trash", [])
    user.setdefault("notifications", [])
    user.setdefault("activity_log", [])
    user.setdefault("created_at", now())
    user.setdefault("role", "user")
    user.setdefault("used_storage", 0)

    os.makedirs(get_user_folder(username), exist_ok=True)
    os.makedirs(os.path.join(get_user_folder(username), "Trash"), exist_ok=True)
    os.makedirs(os.path.join(get_user_folder(username), "Shared"), exist_ok=True)

    save_users(users)

def add_activity(users, username, action):
    users[username]["activity_log"].append({
        "time": now(),
        "action": action
    })
    save_users(users)

def add_notification(users, username, message):
    users[username]["notifications"].append({
        "time": now(),
        "message": message
    })
    save_users(users)

def register(users):
    username = input("Create username: ")
    if username in users:
        print("Username already exists.")
        return

    password = input("Create password: ")
    quota = float(input("Enter storage quota in MB: "))
    role = "admin" if username.lower() == "admin" else "user"

    users[username] = {
        "password": hash_password(password),
        "quota": quota,
        "used_storage": 0,
        "files": [],
        "folders": [],
        "shared_files": [],
        "trash": [],
        "notifications": [],
        "activity_log": [],
        "created_at": now(),
        "role": role
    }

    fix_user_data(users, username)
    print("Account created successfully.")

def login(users):
    username = input("Enter username: ")
    password = input("Enter password: ")
    if username in users and users[username]["password"] == hash_password(password):
        fix_user_data(users, username)
        add_activity(users, username, "Logged in")
        print("Login successful.")
        return username

    print("Invalid username or password.")
    return None

def get_file_path(username, file_info):
    if file_info.get("folder", "Main") == "Main":
        return os.path.join(get_user_folder(username), file_info["name"])
    return os.path.join(get_user_folder(username), file_info["folder"], file_info["name"])

def upload_file(users, username):
    path = input("Enter full file path: ")

    if not os.path.exists(path):
        print("File does not exist.")
        return

    file_name = os.path.basename(path)
    size = os.path.getsize(path) / (1024 * 1024)
    if users[username]["used_storage"] + size > users[username]["quota"]:
        print("Storage quota exceeded.")
        return

    folder = input("Enter folder name or press Enter for Main: ").strip()
    if folder == "":
        folder = "Main"
        destination = os.path.join(get_user_folder(username), file_name)
    else:
        folder_path = os.path.join(get_user_folder(username), folder)
        if not os.path.exists(folder_path):
            print("Folder does not exist.")
            return

        destination = os.path.join(folder_path, file_name)
    if os.path.exists(destination):
        print("File already exists.")
        return

    shutil.copy(path, destination)
    file_info = {
        "name": file_name,
        "size": round(size, 2),
        "folder": folder,
        "type": detect_file_type(file_name),
        "uploaded_at": now(),
        "favorite": False
    }

    users[username]["files"].append(file_info)
    users[username]["used_storage"] += size
    add_activity(users, username, "Uploaded file: " + file_name)
    save_users(users)
    print("File uploaded successfully.")

def show_files(users, username):
    files = users[username]["files"]
    if len(files) == 0:
        print("No files uploaded.")
        return

    print("\nFiles:")
    for file in files:
        star = "★" if file.get("favorite", False) else ""
        print(
            star,
            file["name"],
            "|",
            file["size"],
            "MB |",
            file.get("type", "Unknown"),
            "| Folder:",
            file.get("folder", "Main"),
            "| Uploaded:",
            file.get("uploaded_at", "Unknown")
        )

def sort_files(users, username):
    print("1. Sort by name")
    print("2. Sort by size")
    print("3. Sort by upload date")

    choice = input("Choose: ")
    if choice == "1":
        users[username]["files"].sort(key=lambda x: x["name"].lower())
    elif choice == "2":
        users[username]["files"].sort(key=lambda x: x["size"])
    elif choice == "3":
        users[username]["files"].sort(key=lambda x: x.get("uploaded_at", ""))
    else:
        print("Invalid choice.")
        return
    save_users(users)
    print("Files sorted successfully.")

def search_filters(users, username):
    print("1. Search by name")
    print("2. Search by type")
    print("3. Search by folder")

    choice = input("Choose: ")
    keyword = input("Enter keyword: ").lower()
    found = False
    for file in users[username]["files"]:
        if choice == "1" and keyword in file["name"].lower():
            print(file["name"], "-", file.get("type", "Unknown"))
            found = True
        elif choice == "2" and keyword in file.get("type", "").lower():
            print(file["name"], "-", file.get("type", "Unknown"))
            found = True
        elif choice == "3" and keyword in file.get("folder", "Main").lower():
            print(file["name"], "-", file.get("folder", "Main"))
            found = True

    if not found:
        print("No matching files found.")

def rename_file(users, username):
    old = input("Enter current file name: ")
    new = input("Enter new file name: ")
    if new.strip() == "":
        print("New name cannot be empty.")
        return
    for file in users[username]["files"]:
        if file["name"] == old:
            old_path = get_file_path(username, file)
            if file.get("folder", "Main") == "Main":
                new_path = os.path.join(get_user_folder(username), new)
            else:
                new_path = os.path.join(get_user_folder(username), file["folder"], new)
            if os.path.exists(new_path):
                print("A file with that name already exists.")
                return

            os.rename(old_path, new_path)
            file["name"] = new
            file["type"] = detect_file_type(new)
            add_activity(users, username, "Renamed file: " + old + " to " + new)
            save_users(users)
            print("File renamed successfully.")
            return
    print("File not found.")

def delete_file(users, username):
    file_name = input("Enter file name to move to trash: ")

    for file in users[username]["files"]:
        if file["name"] == file_name:
            old_path = get_file_path(username, file)
            trash_path = os.path.join(get_user_folder(username), "Trash", file_name)
            shutil.move(old_path, trash_path)
            file["deleted_at"] = now()
            users[username]["trash"].append(file)
            users[username]["files"].remove(file)

            add_activity(users, username, "Moved to trash: " + file_name)
            save_users(users)
            print("File moved to trash.")
            return

    print("File not found.")

def show_trash(users, username):
    trash = users[username]["trash"]

    if len(trash) == 0:
        print("Trash is empty.")
        return

    for file in trash:
        print(file["name"], "| Deleted:", file.get("deleted_at", "Unknown"))

def restore_file(users, username):
    file_name = input("Enter file name to restore: ")
    for file in users[username]["trash"]:
        if file["name"] == file_name:
            trash_path = os.path.join(get_user_folder(username), "Trash", file_name)

            if file.get("folder", "Main") == "Main":
                restore_path = os.path.join(get_user_folder(username), file_name)
            else:
                folder_path = os.path.join(get_user_folder(username), file["folder"])
                os.makedirs(folder_path, exist_ok=True)
                restore_path = os.path.join(folder_path, file_name)

            shutil.move(trash_path, restore_path)
            file.pop("deleted_at", None)
            users[username]["files"].append(file)
            users[username]["trash"].remove(file)
            add_activity(users, username, "Restored file: " + file_name)
            save_users(users)
            print("File restored.")
            return
    print("File not found in trash.")

def permanent_delete(users, username):
    file_name = input("Enter file name to permanently delete: ")
    for file in users[username]["trash"]:
        if file["name"] == file_name:
            trash_path = os.path.join(get_user_folder(username), "Trash", file_name)
            if os.path.exists(trash_path):
                os.remove(trash_path)
            users[username]["used_storage"] -= file["size"]
            users[username]["trash"].remove(file)
            add_activity(users, username, "Permanently deleted: " + file_name)
            save_users(users)
            print("File permanently deleted.")
            return
    print("File not found.")

def download_file(users, username):
    file_name = input("Enter file name to download: ")
    destination_folder = input("Enter destination folder path: ")
    if not os.path.exists(destination_folder):
        print("Destination folder does not exist.")
        return
    for file in users[username]["files"]:
        if file["name"] == file_name:
            source = get_file_path(username, file)
            destination = os.path.join(destination_folder, file_name)
            shutil.copy(source, destination)
            add_activity(users, username, "Downloaded file: " + file_name)
            save_users(users)
            print("File downloaded successfully.")
            return
    print("File not found.")

def create_folder(users, username):
    folder = input("Enter folder name: ")
    if folder.strip() == "":
        print("Folder name cannot be empty.")
        return
    path = os.path.join(get_user_folder(username), folder)
    if os.path.exists(path):
        print("Folder already exists.")
        return
    os.mkdir(path)
    users[username]["folders"].append(folder)
    add_activity(users, username, "Created folder: " + folder)
    save_users(users)
    print("Folder created.")

def show_folders(users, username):
    folders = users[username]["folders"]
    if len(folders) == 0:
        print("No folders.")
        return
    for folder in folders:
        print("-", folder)

def share_file(users, username):
    file_name = input("Enter file name to share: ")
    receiver = input("Enter receiver username: ")
    if receiver not in users:
        print("Receiver does not exist.")
        return
    if receiver == username:
        print("Cannot share with yourself.")
        return
    fix_user_data(users, receiver)
    for file in users[username]["files"]:
        if file["name"] == file_name:
            source = get_file_path(username, file)
            shared_folder = os.path.join(get_user_folder(receiver), "Shared")
            destination = os.path.join(shared_folder, file_name)
            shutil.copy(source, destination)
            users[receiver]["shared_files"].append({
                "name": file_name,
                "from": username,
                "shared_at": now()
            })

            add_notification(users, receiver, username + " shared " + file_name + " with you.")
            add_activity(users, username, "Shared file: " + file_name + " with " + receiver)
            save_users(users)
            print("File shared successfully.")
            return
    print("File not found.")

def view_shared_files(users, username):
    shared = users[username]["shared_files"]
    if len(shared) == 0:
        print("No shared files.")
        return
    for file in shared:
        print(file["name"], "| From:", file["from"], "| Shared:", file["shared_at"])

def favorite_file(users, username):
    file_name = input("Enter file name to favourite/unfavourite: ")
    for file in users[username]["files"]:
        if file["name"] == file_name:
            file["favorite"] = not file.get("favorite", False)
            save_users(users)
            if file["favorite"]:
                print("File added to favourites.")
            else:
                print("File removed from favourites.")
            return
    print("File not found.")

def view_favorites(users, username):
    found = False
    for file in users[username]["files"]:
        if file.get("favorite", False):
            print("★", file["name"])
            found = True

    if not found:
        print("No favourite files.")

def storage_info(users, username):
    user = users[username]
    remaining = user["quota"] - user["used_storage"]

    print("Quota:", user["quota"], "MB")
    print("Used:", round(user["used_storage"], 2), "MB")
    print("Remaining:", round(remaining, 2), "MB")

def user_profile(users, username):
    user = users[username]
    print("Username:", username)
    print("Role:", user.get("role", "user"))
    print("Account Created:", user.get("created_at", "Unknown"))
    print("Files Uploaded:", len(user["files"]))
    print("Folders:", len(user["folders"]))
    print("Shared Files Received:", len(user["shared_files"]))
    print("Trash Items:", len(user["trash"]))
    storage_info(users, username)

def view_activity_log(users, username):
    log = users[username]["activity_log"]
    if len(log) == 0:
        print("No activity yet.")
        return
    for item in log:
        print(item["time"], "-", item["action"])

def view_notifications(users, username):
    notes = users[username]["notifications"]
    if len(notes) == 0:
        print("No notifications.")
        return
    for note in notes:
        print(note["time"], "-", note["message"])

def admin_dashboard(users):
    print("\nADMIN DASHBOARD")
    print("Total Users:", len(users))
    total_files = 0
    total_storage = 0
    for username in users:
        total_files += len(users[username].get("files", []))
        total_storage += users[username].get("used_storage", 0)

    print("Total Files:", total_files)
    print("Total Storage Used:", round(total_storage, 2), "MB")
    print("\nUsers:")
    for username in users:
        print(
            username,
            "| Role:",
            users[username].get("role", "user"),
            "| Files:",
            len(users[username].get("files", [])),
            "| Used:",
            round(users[username].get("used_storage", 0), 2),
            "MB"
        )

def user_menu(users, username):
    while True:
        clear_screen()
        print("--- USER MENU ---")
        print("Logged in as:", username)
        print("1. Upload File")
        print("2. Show Files")
        print("3. Sort Files")
        print("4. Search Filters")
        print("5. Rename File")
        print("6. Delete File")
        print("7. Show Trash")
        print("8. Restore File")
        print("9. Permanent Delete")
        print("10. Download File")
        print("11. Create Folder")
        print("12. Show Folders")
        print("13. Share File")
        print("14. View Shared Files")
        print("15. Favourite / Unfavourite File")
        print("16. View Favourites")
        print("17. Storage Info")
        print("18. Profile")
        print("19. Activity Log")
        print("20. Notifications")
        if users[username].get("role") == "admin":
            print("21. Admin Dashboard")
            print("22. Logout")
        else:
            print("21. Logout")

        choice = input("Choose: ")
        clear_screen()

        if choice == "1":
            upload_file(users, username)
        elif choice == "2":
            show_files(users, username)
        elif choice == "3":
            sort_files(users, username)
        elif choice == "4":
            search_filters(users, username)
        elif choice == "5":
            rename_file(users, username)
        elif choice == "6":
            delete_file(users, username)
        elif choice == "7":
            show_trash(users, username)
        elif choice == "8":
            restore_file(users, username)
        elif choice == "9":
            permanent_delete(users, username)
        elif choice == "10":
            download_file(users, username)
        elif choice == "11":
            create_folder(users, username)
        elif choice == "12":
            show_folders(users, username)
        elif choice == "13":
            share_file(users, username)
        elif choice == "14":
            view_shared_files(users, username)
        elif choice == "15":
            favorite_file(users, username)
        elif choice == "16":
            view_favorites(users, username)
        elif choice == "17":
            storage_info(users, username)
        elif choice == "18":
            user_profile(users, username)
        elif choice == "19":
            view_activity_log(users, username)
        elif choice == "20":
            view_notifications(users, username)
        elif choice == "21" and users[username].get("role") == "admin":
            admin_dashboard(users)
        elif choice == "21" and users[username].get("role") != "admin":
            print("Logged out.")
            pause()
            break
        elif choice == "22" and users[username].get("role") == "admin":
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

        print("=== MINI CLOUD STORAGE SIMULATOR ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ")
        clear_screen()
        if choice == "1":
            register(users)
        elif choice == "2":
            current_user = login(users)
            if current_user:
                pause()
                user_menu(users, current_user)
        elif choice == "3":
            print("Program closed.")
            break
        else:
            print("Invalid choice.")
        pause()


main()
