from enum import Enum

class StatusDataSentDb(Enum):
    STORED = "STORED"
    EXISTS = "EXISTS"
    MISSING_FIELD = "MISSING_FIELD"
    ERROR = "ERROR"

class DataType(Enum):
    # Basic Numeric Types
    INTEGER = "INTEGER"
    UINTEGER = "UINTEGER"
    DECIMAL = "DECIMAL"
    DOUBLE = "DOUBLE"
    BIG_INTEGER = "BIG_INTEGER"
    SMALL_INTEGER = "SMALL_INTEGER"
    BYTE = "BYTE"
    SHORT = "SHORT"
    LONG = "LONG"
    CURRENCY = "CURRENCY"

    # Text & String Types
    STRING = "STRING"
    MULTI_STRING = "MULTI_STRING"
    CHAR = "CHAR"
    TEXT = "TEXT"
    RICH_TEXT = "RICH_TEXT"
    PASSWORD = "PASSWORD"
    SLUG = "SLUG"

    # Boolean & Date Types
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    YEAR = "YEAR"
    MONTH = "MONTH"

    # Complex Data Structures
    LIST = "LIST"
    SET = "SET"
    ARRAY = "ARRAY"
    TUPLE = "TUPLE"
    MAP = "MAP"
    DICTIONARY = "DICTIONARY"
    JSON = "JSON"
    XML = "XML"
    YAML = "YAML"

    # Identifiers & References
    UUID = "UUID"
    OBJECT_ID = "OBJECT_ID"
    REFERENCE = "REFERENCE"
    HASH = "HASH"
    ENUM = "ENUM"

    # Specialized Types
    EMAIL = "EMAIL"
    URL = "URL"
    DOMAIN = "DOMAIN"
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    MAC_ADDRESS = "MAC_ADDRESS"
    FILE = "FILE"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    BARCODE = "BARCODE"
    GEOPOINT = "GEOPOINT"
    COLOR = "COLOR"
    HEX = "HEX"
    BINARY = "BINARY"
    COMPRESSED = "COMPRESSED"

    # ======= Helper Methods =======
    
    def is_numeric(self):
        """Check if the data type is numeric (integer, decimal, etc.)."""
        return self in {
            DataType.INTEGER, DataType.UINTEGER, DataType.DECIMAL, DataType.DOUBLE,
            DataType.BIG_INTEGER, DataType.SMALL_INTEGER, DataType.BYTE,
            DataType.SHORT, DataType.LONG, DataType.CURRENCY
        }
    
    def is_text(self):
        """Check if the data type is text-based."""
        return self in {
            DataType.STRING, DataType.MULTI_STRING, DataType.CHAR, DataType.TEXT,
            DataType.RICH_TEXT, DataType.PASSWORD, DataType.SLUG
        }

    def is_boolean(self):
        """Check if the data type is boolean."""
        return self == DataType.BOOLEAN

    def is_date_time(self):
        """Check if the data type is related to date or time."""
        return self in {
            DataType.DATE, DataType.TIME, DataType.DATETIME, 
            DataType.TIMESTAMP, DataType.YEAR, DataType.MONTH
        }

    def is_collection(self):
        """Check if the data type is a collection (list, set, array, etc.)."""
        return self in {
            DataType.LIST, DataType.SET, DataType.ARRAY, DataType.TUPLE, 
            DataType.MAP, DataType.DICTIONARY
        }

    def is_serializable(self):
        """Check if the data type is a structured serializable format."""
        return self in {DataType.JSON, DataType.XML, DataType.YAML}

    def is_identifier(self):
        """Check if the data type represents an identifier or key."""
        return self in {
            DataType.UUID, DataType.OBJECT_ID, DataType.REFERENCE, 
            DataType.HASH, DataType.ENUM
        }

    def is_network_related(self):
        """Check if the data type is related to networking."""
        return self in {
            DataType.EMAIL, DataType.URL, DataType.DOMAIN, 
            DataType.IPV4, DataType.IPV6, DataType.MAC_ADDRESS
        }

    def is_media(self):
        """Check if the data type is media-related (file, image, audio, video)."""
        return self in {
            DataType.FILE, DataType.IMAGE, DataType.AUDIO, DataType.VIDEO
        }

    def is_special(self):
        """Check if the data type is a special case."""
        return self in {
            DataType.BARCODE, DataType.GEOPOINT, DataType.COLOR,
            DataType.HEX, DataType.BINARY, DataType.COMPRESSED
        }

from enum import Enum

class DataCategory(Enum):
    # Personal Identification
    NAME = "NAME"
    SURNAME = "SURNAME"
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT_NUMBER = "PASSPORT_NUMBER"
    TAX_ID = "TAX_ID"
    GENDER = "GENDER"
    AGE = "AGE"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    
    # Contact Information
    EMAIL = "EMAIL"
    MOBILE_PHONE = "MOBILE_PHONE"
    HOME_PHONE = "HOME_PHONE"
    WORK_PHONE = "WORK_PHONE"
    POSTAL_ADDRESS = "POSTAL_ADDRESS"
    CITY = "CITY"
    POSTAL_CODE = "POSTAL_CODE"
    COUNTRY = "COUNTRY"
    RESIDENCE_COUNTRY = "RESIDENCE_COUNTRY"

    # Financial & Banking
    IBAN = "IBAN"
    BANK_ACCOUNT_NUMBER = "BANK_ACCOUNT_NUMBER"
    CREDIT_CARD_NUMBER = "CREDIT_CARD_NUMBER"
    SWIFT_CODE = "SWIFT_CODE"
    CRYPTO_WALLET = "CRYPTO_WALLET"

    # Vehicles & Transportation
    CAR_MODEL = "CAR_MODEL"
    MAIN_CAR_LICENSE_PLATE = "MAIN_CAR_LICENSE_PLATE"
    SECONDARY_CAR_LICENSE_PLATE = "SECONDARY_CAR_LICENSE_PLATE"
    DRIVER_LICENSE_NUMBER = "DRIVER_LICENSE_NUMBER"

    # Work & Education
    JOB_TITLE = "JOB_TITLE"
    COMPANY_NAME = "COMPANY_NAME"
    EDUCATION_LEVEL = "EDUCATION_LEVEL"
    UNIVERSITY = "UNIVERSITY"
    DEGREE = "DEGREE"

    # Health & Medical
    BLOOD_TYPE = "BLOOD_TYPE"
    ALLERGIES = "ALLERGIES"
    MEDICAL_CONDITIONS = "MEDICAL_CONDITIONS"
    EMERGENCY_CONTACT = "EMERGENCY_CONTACT"
    HEALTH_INSURANCE_NUMBER = "HEALTH_INSURANCE_NUMBER"

    # Digital & Security
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    WEBSITE_LOGIN = "WEBSITE_LOGIN"
    SOCIAL_MEDIA_PROFILE = "SOCIAL_MEDIA_PROFILE"
    WIFI_CREDENTIALS = "WIFI_CREDENTIALS"
    TWO_FACTOR_AUTH_CODE = "TWO_FACTOR_AUTH_CODE"

    # Social & Preferences
    PET_ANIMAL = "PET_ANIMAL"
    FAVORITE_COLOR = "FAVORITE_COLOR"
    HOBBIES = "HOBBIES"
    FAVORITE_MUSIC_GENRE = "FAVORITE_MUSIC_GENRE"

    # Ratings & Scores
    SCORE = "SCORE"
    RATING = "RATING"
    REVIEW = "REVIEW"

    # Miscellaneous
    CUSTOM_NOTE = "CUSTOM_NOTE"
    BARCODE = "BARCODE"
    QR_CODE = "QR_CODE"
    LOCATION_COORDINATES = "LOCATION_COORDINATES"
    EVENT_DATE = "EVENT_DATE"

    def __str__(self):
        return self.value

    # ======= Helper Methods =======

    def is_personal_info(self):
        return self in {
            DataCategory.NAME, DataCategory.SURNAME, DataCategory.NATIONAL_ID,
            DataCategory.PASSPORT_NUMBER, DataCategory.TAX_ID, DataCategory.GENDER,
            DataCategory.AGE, DataCategory.DATE_OF_BIRTH
        }

    def is_contact_info(self):
        return self in {
            DataCategory.EMAIL, DataCategory.MOBILE_PHONE, DataCategory.HOME_PHONE,
            DataCategory.WORK_PHONE, DataCategory.POSTAL_ADDRESS, DataCategory.CITY,
            DataCategory.POSTAL_CODE, DataCategory.COUNTRY, DataCategory.RESIDENCE_COUNTRY
        }

    def is_financial_info(self):
        return self in {
            DataCategory.IBAN, DataCategory.BANK_ACCOUNT_NUMBER, DataCategory.CREDIT_CARD_NUMBER,
            DataCategory.SWIFT_CODE, DataCategory.CRYPTO_WALLET
        }

    def is_vehicle_info(self):
        return self in {
            DataCategory.CAR_MODEL, DataCategory.MAIN_CAR_LICENSE_PLATE,
            DataCategory.SECONDARY_CAR_LICENSE_PLATE, DataCategory.DRIVER_LICENSE_NUMBER
        }

    def is_professional_info(self):
        return self in {
            DataCategory.JOB_TITLE, DataCategory.COMPANY_NAME, DataCategory.EDUCATION_LEVEL,
            DataCategory.UNIVERSITY, DataCategory.DEGREE
        }

    def is_health_info(self):
        return self in {
            DataCategory.BLOOD_TYPE, DataCategory.ALLERGIES, DataCategory.MEDICAL_CONDITIONS,
            DataCategory.EMERGENCY_CONTACT, DataCategory.HEALTH_INSURANCE_NUMBER
        }

    def is_security_info(self):
        return self in {
            DataCategory.USERNAME, DataCategory.PASSWORD, DataCategory.WEBSITE_LOGIN,
            DataCategory.SOCIAL_MEDIA_PROFILE, DataCategory.WIFI_CREDENTIALS,
            DataCategory.TWO_FACTOR_AUTH_CODE
        }

    def is_miscellaneous(self):
        return self in {
            DataCategory.CUSTOM_NOTE, DataCategory.BARCODE, DataCategory.QR_CODE,
            DataCategory.LOCATION_COORDINATES, DataCategory.EVENT_DATE
        }