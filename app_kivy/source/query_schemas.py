# Fields
SELECT_ALL_FIELDS = "SELECT `key`, `value`, `creation_date` FROM fields"
SELECT_ONE_FIELD_BY_ID = "SELECT `key`, `value`, `creation_date` FROM fields WHERE `id` = ?"
SELECT_ONE_FIELD_BY_KEY = "SELECT `key`, `value`, `creation_date` FROM fields WHERE `key` = ?"
COUNT_FIELDS_BY_KEY = "SELECT COUNT(*) FROM fields WHERE `key` = ?"
INSERT_FIELD = "INSERT INTO fields (`key`, value, custom_name) VALUES (?, ?, ?)"
DELETE_FIELD_BY_KEY = "DELETE FROM fields WHERE `key` = ?"
# Users
SELECT_ALL_USERS = "SELECT username, email, creation_date FROM users"
SELECT_ONE_USER_BY_ID = "SELECT username, email, phone_number, phone_extension, creation_date FROM users WHERE id = ?"
SELECT_ONE_USER_BY_USERNAME = "SELECT username, email, creation_date FROM users WHERE `username` = ?"
COUNT_USERS_BY_USERNAME = "SELECT COUNT(*) FROM users WHERE username = ?"
INSERT_USER = "INSERT INTO users (username, email, phone_number, phone_extension) VALUES (?, ?, ?, ?)"
DELETE_USER_BY_USERNAME = "DELETE FROM users WHERE username = ?"