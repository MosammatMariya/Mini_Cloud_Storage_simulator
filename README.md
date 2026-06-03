# Mini_Cloud_Storage_simulator
The Mini Cloud Storage Simulator is a Python-based application designed to simulate the core functionalities of cloud storage platforms such as Google Drive and Dropbox. The system allows users to register and log into personal accounts, upload and download real files, create folders, search and rename files, and manage storage quotas. Additional features include file sharing between users, upload timestamps, trash bin functionality with restore and permanent delete options, and secure local file storage. The project uses JSON for permanent data storage and demonstrates important programming concepts such as file handling, authentication, CRUD operations, and storage management using Python.

Features:
- User Registration and Login
- Real File Upload
- Folder Management
- File Sharing
- Download Files
- Trash Bin System
- Restore Deleted Files
- Permanent File Deletion
- Storage Quota Management
- Upload Timestamps

Technologies Used:
- Python
- JSON
- os module
- shutil module
- datetime module


#Advanced Features Added
To enhance the functionality and realism of the Mini Cloud Storage Simulator, several advanced features were implemented beyond the basic file management operations.

- Password Encryption
A password encryption system was added using SHA-256 hashing. Instead of storing plain text passwords, the system stores encrypted hash values, improving   security and protecting user credentials from unauthorized access.

- File Type Detection
The system automatically identifies the type of each uploaded file based on its extension. Supported categories include images, PDF documents, Word documents, audio files, video files, and text files. This helps users organize and manage files more effectively.

- File Sorting
Users can sort files by name, file size, or upload date. This feature improves file organization and allows users to quickly locate important files.

- Activity Log
An activity logging system records major user actions such as login, file upload, download, sharing, folder creation, deletion, and restoration. Each activity is stored with a timestamp, creating a complete history of user operations.

- Search Filters
Advanced search functionality was added to allow users to search files by filename, file type, or folder location. This provides faster and more efficient file retrieval.

- Notifications System
Users receive notifications when another user shares a file with them. Each notification contains information about the sender, the shared file, and the time the file was shared.

- Favourite Files
A favourites feature allows users to mark important files for quick access. Starred files can be viewed separately, making frequently used documents easier to locate.

- User Profile
A user profile section displays account information, including username, account creation date, number of uploaded files, number of folders, storage usage, and shared file statistics.

- Admin Dashboard
An administrative dashboard was introduced to monitor system usage. The dashboard provides information such as total users, total uploaded files, storage consumption, and user activity statistics. This feature supports system management and monitoring.

- Enhanced Security and Monitoring
The combination of password encryption, activity logging, notifications, and administrative monitoring improves both the security and reliability of the cloud storage system while providing a more realistic cloud storage experience.
