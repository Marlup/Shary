# Dimensions
LOGIN_WIDTH = 1800
LOGIN_HEIGHT = 1200
FIELDS_WIDTH = 1800
FIELDS_HEIGHT = 1200
USERS_WIDTH = 1800
USERS_HEIGHT = 1200
ROW_HEIGHT = 40  # 🔧 Constant row height
DEFAULT_ROW_KEY_WIDTH = 50
DEFAULT_ROW_VALUE_WIDTH = 200
DEFAULT_ROW_REST_WIDTH = 50
DEFAULT_NUM_ROWS_PAGE = 20
DEFAULT_USE_PAGINATION = False

# Formats
FILE_FORMATS = ("json", "csv", "xml", "yaml")
FIELD_HEADERS = ("key", "value", "creation_date")
USER_HEADERS = ("username", "email", "creation_date")

# Predefined messages
MSG_DEFAULT_SEND_FILENAME = "shary_fields_from_"
MSG_DEFAULT_REQUEST_FILENAME = "shary_fields_request_from_"
MSG_DELETION_WARNING = "Are you sure you want to delete the following selected fields?\n"

SMTP_SERVER = "smtp.gmail.com"
COLLECTION_SHARE_NAME = "sharing"
SMTP_SSL_PORT = 465
SMTP_TLS_PORT = 587