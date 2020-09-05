# Database
DATABASE_NAME = "file_share"
USER_COLLECTION = "user_basic_data"
AUTH_COLLECTION = "auth_tokens"
FILES_COLLECTION = "files"
FILES_HISTORY = "files_downloads"
DATABASE_URL = "mongodb://localhost:27017/file_share."

# cookies
AUTH_COOKIE_DURATION = 30 * 24 * 60 * 60
AUTH_COOKIE_LENGTH = 10

# files
MAX_FILE_SIZE = 300 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "gif", "png", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "csv"}
FILE_HASH_LENGTH = 10
