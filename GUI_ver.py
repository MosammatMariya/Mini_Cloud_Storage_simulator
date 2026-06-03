import os
import json
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

DATA_FILE = "users.json"

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
    user = users[username]
    user.setdefault("files", [])
    user.setdefault("folders", [])
    user.setdefault("shared_files", [])
    user.setdefault("trash", [])
    user.setdefault("used_storage", 0)

    os.makedirs(get_user_folder(username), exist_ok=True)
    os.makedirs(os.path.join(get_user_folder(username), "Shared"), exist_ok=True)
    os.makedirs(os.path.join(get_user_folder(username), "Trash"), exist_ok=True)
    save_users(users)

def get_file_path(username, file_info):
    folder = file_info.get("folder", "Main")
    if folder == "Main":
        return os.path.join(get_user_folder(username), file_info["name"])
    else:
        return os.path.join(get_user_folder(username), folder, file_info["name"])

class MiniCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Cloud Storage Simulator")
        self.root.geometry("700x550")
        self.users = load_users()
        self.current_user = None
        self.show_start_page()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_start_page(self):
        self.clear()
        tk.Label(self.root, text="Mini Cloud Storage Simulator", font=("Arial", 22, "bold")).pack(pady=30)
        tk.Button(self.root, text="Register", width=30, command=self.show_register_page).pack(pady=10)
        tk.Button(self.root, text="Login", width=30, command=self.show_login_page).pack(pady=10)
        tk.Button(self.root, text="Exit", width=30, command=self.root.destroy).pack(pady=10)

    def show_register_page(self):
        self.clear()
        tk.Label(self.root, text="Register Account", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Username").pack()
        username_entry = tk.Entry(self.root, width=35)
        username_entry.pack(pady=5)
        tk.Label(self.root, text="Password").pack()
        password_entry = tk.Entry(self.root, width=35, show="*")
        password_entry.pack(pady=5)
        tk.Label(self.root, text="Storage Quota MB").pack()
        quota_entry = tk.Entry(self.root, width=35)
        quota_entry.pack(pady=5)

        def register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            try:
                quota = float(quota_entry.get())
            except:
                messagebox.showerror("Error", "Quota must be a number.")
                return
            if username == "" or password == "":
                messagebox.showerror("Error", "Username and password cannot be empty.")
                return
            if username in self.users:
                messagebox.showerror("Error", "Username already exists.")
                return

            self.users[username] = {
                "password": password,
                "quota": quota,
                "used_storage": 0,
                "files": [],
                "folders": [],
                "shared_files": [],
                "trash": []
            }

            os.makedirs(get_user_folder(username), exist_ok=True)
            os.makedirs(os.path.join(get_user_folder(username), "Shared"), exist_ok=True)
            os.makedirs(os.path.join(get_user_folder(username), "Trash"), exist_ok=True)
            save_users(self.users)
            messagebox.showinfo("Success", "Account created successfully.")
            self.show_start_page()
        tk.Button(self.root, text="Create Account", width=25, command=register).pack(pady=15)
        tk.Button(self.root, text="Back", width=25, command=self.show_start_page).pack()

    def show_login_page(self):
        self.clear()
        tk.Label(self.root, text="Login", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Username").pack()
        username_entry = tk.Entry(self.root, width=35)
        username_entry.pack(pady=5)

        tk.Label(self.root, text="Password").pack()
        password_entry = tk.Entry(self.root, width=35, show="*")
        password_entry.pack(pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if username in self.users and self.users[username]["password"] == password:
                self.current_user = username
                fix_user_data(self.users, username)
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        tk.Button(self.root, text="Login", width=25, command=login).pack(pady=15)
        tk.Button(self.root, text="Back", width=25, command=self.show_start_page).pack()

    def show_dashboard(self):
        self.clear()
        tk.Label(
            self.root,
            text="Welcome, " + self.current_user,
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        buttons = [
            ("Upload File", self.upload_file),
            ("Show Files", self.show_files),
            ("Search File", self.search_file),
            ("Rename File", self.rename_file),
            ("Delete File to Trash", self.delete_file),
            ("Show Trash", self.show_trash),
            ("Restore File", self.restore_file),
            ("Permanent Delete", self.permanent_delete),
            ("Download File", self.download_file),
            ("Create Folder", self.create_folder),
            ("Show Folders", self.show_folders),
            ("Share File", self.share_file),
            ("View Shared Files", self.view_shared_files),
            ("Storage Info", self.storage_info),
            ("Logout", self.logout)
        ]

        for text, command in buttons:
            tk.Button(self.root, text=text, width=35, command=command).pack(pady=3)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path == "":
            return
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        user = self.users[self.current_user]
        if user["used_storage"] + file_size > user["quota"]:
            messagebox.showerror("Error", "Storage quota exceeded.")
            return
        folder_name = simpledialog.askstring(
            "Upload Location",
            "Enter folder name or leave blank for Main:"
        )

        if folder_name is None or folder_name.strip() == "":
            folder_name = "Main"
            destination = os.path.join(get_user_folder(self.current_user), file_name)
        else:
            folder_path = os.path.join(get_user_folder(self.current_user), folder_name)
            if not os.path.exists(folder_path):
                messagebox.showerror("Error", "Folder does not exist.")
                return

            destination = os.path.join(folder_path, file_name)
        if os.path.exists(destination):
            messagebox.showerror("Error", "A file with this name already exists.")
            return

        shutil.copy(file_path, destination)
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user["files"].append({
            "name": file_name,
            "size": round(file_size, 2),
            "folder": folder_name,
            "uploaded_at": upload_time
        })
        user["used_storage"] += file_size
        save_users(self.users)
        messagebox.showinfo("Success", "File uploaded successfully.")

    def show_files(self):
        self.clear()
        tk.Label(self.root, text="My Files", font=("Arial", 18, "bold")).pack(pady=15)
        files = self.users[self.current_user]["files"]
        if len(files) == 0:
            tk.Label(self.root, text="No files uploaded.").pack()
        else:
            for file_info in files:
                text = (
                    file_info["name"]
                    + " | "
                    + str(file_info["size"])
                    + " MB | Folder: "
                    + file_info.get("folder", "Main")
                    + " | Uploaded: "
                    + file_info.get("uploaded_at", "Old File")
                )
               tk.Label(self.root, text=text).pack(anchor="w", padx=30)
        tk.Button(self.root, text="Back", command=self.show_dashboard).pack(pady=20)

    def search_file(self):
        keyword = simpledialog.askstring("Search File", "Enter keyword:")
        if keyword is None:
            return
        results = []
        for file_info in self.users[self.current_user]["files"]:
            if keyword.lower() in file_info["name"].lower():
                results.append(file_info["name"])

        if len(results) == 0:
            messagebox.showinfo("Search Results", "No matching files found.")
        else:
            messagebox.showinfo("Search Results", "\n".join(results))

    def rename_file(self):
        old_name = simpledialog.askstring("Rename File", "Enter current file name:")
        if old_name is None or old_name.strip() == "":
            return

        new_name = simpledialog.askstring("Rename File", "Enter new file name:")
        if new_name is None or new_name.strip() == "":
            messagebox.showerror("Error", "New file name cannot be empty.")
            return

        for file_info in self.users[self.current_user]["files"]:
            if file_info["name"] == old_name:
                old_path = get_file_path(self.current_user, file_info)

                folder = file_info.get("folder", "Main")
                if folder == "Main":
                    new_path = os.path.join(get_user_folder(self.current_user), new_name)
                else:
                    new_path = os.path.join(get_user_folder(self.current_user), folder, new_name)
                if os.path.exists(new_path):
                    messagebox.showerror("Error", "A file with that name already exists.")
                    return

                os.rename(old_path, new_path)
                file_info["name"] = new_name
                save_users(self.users)
                messagebox.showinfo("Success", "File renamed successfully.")
               return
        messagebox.showerror("Error", "File not found.")

    def delete_file(self):
        file_name = simpledialog.askstring("Delete File", "Enter file name:")
        if file_name is None:
            return

        files = self.users[self.current_user]["files"]
        for file_info in files:
            if file_info["name"] == file_name:
                old_path = get_file_path(self.current_user, file_info)
                trash_folder = os.path.join(get_user_folder(self.current_user), "Trash")
                os.makedirs(trash_folder, exist_ok=True)
                new_path = os.path.join(trash_folder, file_name)
                if os.path.exists(old_path):
                    shutil.move(old_path, new_path)

                file_info["deleted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.users[self.current_user]["trash"].append(file_info)
                files.remove(file_info)
                save_users(self.users)
                messagebox.showinfo("Success", "File moved to trash.")
                return

        messagebox.showerror("Error", "File not found.")

    def show_trash(self):
        self.clear()
        tk.Label(self.root, text="Trash Bin", font=("Arial", 18, "bold")).pack(pady=15)
        trash = self.users[self.current_user]["trash"]
        if len(trash) == 0:
            tk.Label(self.root, text="Trash is empty.").pack()
        else:
            for file_info in trash:
                text = (
                    file_info["name"]
                    + " | "
                    + str(file_info["size"])
                    + " MB | Deleted: "
                    + file_info.get("deleted_at", "Unknown")
                )
                tk.Label(self.root, text=text).pack(anchor="w", padx=30)
        tk.Button(self.root, text="Back", command=self.show_dashboard).pack(pady=20)

    def restore_file(self):
        file_name = simpledialog.askstring("Restore File", "Enter file name:")
        if file_name is None:
            return

        trash = self.users[self.current_user]["trash"]
        for file_info in trash:
            if file_info["name"] == file_name:
                trash_path = os.path.join(get_user_folder(self.current_user), "Trash", file_name)

                folder = file_info.get("folder", "Main")
                if folder == "Main":
                    restore_path = os.path.join(get_user_folder(self.current_user), file_name)
                else:
                    folder_path = os.path.join(get_user_folder(self.current_user), folder)
                    os.makedirs(folder_path, exist_ok=True)
                    restore_path = os.path.join(folder_path, file_name)

                if os.path.exists(restore_path):
                    messagebox.showerror("Error", "A file with that name already exists.")
                    return

                shutil.move(trash_path, restore_path)
                if "deleted_at" in file_info:
                    del file_info["deleted_at"]

                self.users[self.current_user]["files"].append(file_info)
                trash.remove(file_info)
                save_users(self.users)
                messagebox.showinfo("Success", "File restored successfully.")
                return
        messagebox.showerror("Error", "File not found in trash.")
      
    def permanent_delete(self):
        file_name = simpledialog.askstring("Permanent Delete", "Enter file name:")
        if file_name is None:
            return

        trash = self.users[self.current_user]["trash"]
        for file_info in trash:
            if file_info["name"] == file_name:
                trash_path = os.path.join(get_user_folder(self.current_user), "Trash", file_name)
                if os.path.exists(trash_path):
                    os.remove(trash_path)

                self.users[self.current_user]["used_storage"] -= file_info["size"]
                trash.remove(file_info)
                save_users(self.users)
                messagebox.showinfo("Success", "File permanently deleted.")
                return

        messagebox.showerror("Error", "File not found in trash.")

    def download_file(self):
        file_name = simpledialog.askstring("Download File", "Enter file name:")
        if file_name is None:
            return

        destination_folder = filedialog.askdirectory()
        if destination_folder == "":
            return

        for file_info in self.users[self.current_user]["files"]:
            if file_info["name"] == file_name:
                source_path = get_file_path(self.current_user, file_info)
                destination = os.path.join(destination_folder, file_name)

                shutil.copy(source_path, destination)
                messagebox.showinfo("Success", "File downloaded successfully.")
                return

        messagebox.showerror("Error", "File not found.")

    def create_folder(self):
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name is None or folder_name.strip() == "":
            messagebox.showerror("Error", "Folder name cannot be empty.")
            return

        folder_path = os.path.join(get_user_folder(self.current_user), folder_name)
        if os.path.exists(folder_path):
            messagebox.showerror("Error", "Folder already exists.")
            return

        os.mkdir(folder_path)
        self.users[self.current_user]["folders"].append(folder_name)
        save_users(self.users)
        messagebox.showinfo("Success", "Folder created successfully.")

    def show_folders(self):
        folders = self.users[self.current_user]["folders"]
        if len(folders) == 0:
            messagebox.showinfo("Folders", "No folders created.")
        else:
            messagebox.showinfo("Folders", "\n".join(folders))

    def share_file(self):
        file_name = simpledialog.askstring("Share File", "Enter file name to share:")
        if file_name is None:
            return

        receiver = simpledialog.askstring("Share File", "Enter receiver username:")
        if receiver is None:
            return

        if receiver not in self.users:
            messagebox.showerror("Error", "Receiver does not exist.")
            return

        if receiver == self.current_user:
            messagebox.showerror("Error", "You cannot share with yourself.")
            return

        fix_user_data(self.users, receiver)
        for file_info in self.users[self.current_user]["files"]:
            if file_info["name"] == file_name:
                source_path = get_file_path(self.current_user, file_info)
                shared_folder = os.path.join(get_user_folder(receiver), "Shared")
                os.makedirs(shared_folder, exist_ok=True)
                destination = os.path.join(shared_folder, file_name)
                shutil.copy(source_path, destination)

                self.users[receiver]["shared_files"].append({
                    "name": file_name,
                    "from": self.current_user,
                    "shared_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                save_users(self.users)
                messagebox.showinfo("Success", "File shared successfully.")
                return

        messagebox.showerror("Error", "File not found.")

    def view_shared_files(self):
        self.clear()
        tk.Label(self.root, text="Shared With Me", font=("Arial", 18, "bold")).pack(pady=15)
        shared = self.users[self.current_user]["shared_files"]
        if len(shared) == 0:
            tk.Label(self.root, text="No shared files.").pack()
        else:
            for file_info in shared:
                text = (
                    file_info["name"]
                    + " | Shared by: "
                    + file_info["from"]
                    + " | Shared at: "
                    + file_info.get("shared_at", "Unknown")
                )
                tk.Label(self.root, text=text).pack(anchor="w", padx=30)
        tk.Button(self.root, text="Back", command=self.show_dashboard).pack(pady=20)

    def storage_info(self):
        user = self.users[self.current_user]
        remaining = user["quota"] - user["used_storage"]
        message = (
            "Total Quota: " + str(user["quota"]) + " MB\n"
            "Used Storage: " + str(round(user["used_storage"], 2)) + " MB\n"
            "Remaining Storage: " + str(round(remaining, 2)) + " MB"
        )
        messagebox.showinfo("Storage Information", message)

    def logout(self):
        self.current_user = None
        self.show_start_page()

root = tk.Tk()
app = MiniCloudApp(root)
root.mainloop()
