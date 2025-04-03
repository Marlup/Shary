# Dimensions
FIELDS_HEIGHT = 1200
FIELDS_WIDTH = 1800
LOGIN_HEIGHT = 1200
LOGIN_WIDTH = 1800
ROW_HEIGHT = 40  # 🔧 Constant row height
USERS_HEIGHT = 1200
USERS_WIDTH = 1800
DEFAULT_NUM_ROWS_PAGE = 20
DEFAULT_ROW_KEY_WIDTH = 50
DEFAULT_ROW_REST_WIDTH = 50
DEFAULT_ROW_VALUE_WIDTH = 200
DEFAULT_USE_PAGINATION = False

# Time values
TIME_DOCUMENT_ALIVE = 24 * 60 * 60 # 3600s

# Formats
FIELD_HEADERS = ("key", "value", "creation_date")
FILE_FORMATS = ("json", "csv", "xml", "yaml")
USER_HEADERS = ("username", "email", "creation_date")

# Names
SCREEN_NAME_FIELD = "field"
SCREEN_NAME_FILE_VISUALIZER = "file_visualizer"
SCREEN_NAME_LOGIN = "login"
SCREEN_NAME_REQUEST = "request"
SCREEN_NAME_USER = "user"
SCREEN_NAME_USER_CREATION = "user_creation"
APPLICATION_NAME = "Shary"

# Networks (HTTP, SMTP, ...)
SMTP_SERVER = "smtp.gmail.com"
FIREBASE_HOST = "localhost"
FIREBASE_PORT = "5001"
FIREBASE_APP_ID = "shary-21b61"
NAME_GC_LOCATION_HOST = "us-central1"
COLLECTION_SHARE_NAME = "sharing"
SMTP_SSL_PORT = 465
SMTP_TLS_PORT = 587

# Paths
PATH_DB = "./shary_demo.db"
PATH_PRIVATE_KEY = "./data/security/private_key.pem"
PATH_PUBLIC_KEY = "./data/security/public_key.pem"
PATH_SECRET_KEY = "./data/security/secret.txt"
PATH_ENV_VARIABLES = "./data/authentication/.env"
# Constants for KV file paths
PATH_SCHEMA_FIELD = "./ui_layouts/field.kv"
PATH_SCHEMA_USER = "./ui_layouts/user.kv"
PATH_SCHEMA_LOGIN = "./ui_layouts/login.kv"
PATH_SCHEMA_REQUEST = "./ui_layouts/request.kv"
PATH_SCHEMA_USER_CREATION = "./ui_layouts/user_creation.kv"
PATH_SCHEMA_FILE_VISUALIZER = "./ui_layouts/file_visualizer.kv"
PATH_SCHEMA_FIELD_DIALOG = "./ui_layouts/add_field_dialog.kv"
PATH_SCHEMA_SEND_EMAIL_DIALOG = "./ui_layouts/send_email_dialog.kv"
PATH_SCHEMA_CHANNEL_CONTENT_DIALOG = "./ui_layouts/select_channel_content.kv"
PATH_SCHEMA_USER_DIALOG = "./ui_layouts/add_user_dialog.kv"
PATH_SCHEMA_REQUEST_DIALOG = "./ui_layouts/add_request_dialog.kv"
# For data directories
PATH_DATA_AUTHENTICATION = "./data/authentication"
PATH_DATA_DOWNLOAD = "./data/download"
PATH_DATA_SECURITY = "./data/security"

KV_PATHS_OTHERS = [
    PATH_SCHEMA_FIELD,
    PATH_SCHEMA_USER,
    PATH_SCHEMA_REQUEST,
    PATH_SCHEMA_FILE_VISUALIZER
]

# Predefined messages
MSG_DEFAULT_SEND_FILENAME = "shary_fields_from_"
MSG_DEFAULT_REQUEST_FILENAME = "shary_fields_request_from_"
MSG_DELETION_WARNING = "Are you sure you want to delete these fields?\n"