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

# Networks (HTTP, SMTP, ...)
SMTP_SERVER = "smtp.gmail.com"
COLLECTION_SHARE_NAME = "sharing"
SMTP_SSL_PORT = 465
SMTP_TLS_PORT = 587

# Paths
PATH_FILE_STORAGE = "./data"

# Predefined messages
MSG_DEFAULT_SEND_FILENAME = "shary_fields_from_"
MSG_DEFAULT_REQUEST_FILENAME = "shary_fields_request_from_"
MSG_DELETION_WARNING = "Are you sure you want to delete these fields?\n"