# Fields
SELECT_ALL_FIELDS = "SELECT `key`, `value`, `creation_date` FROM fields"
SELECT_ONE_FIELD_BY_ID = "SELECT `key`, `value`, `creation_date` FROM fields WHERE `id` = %s"
SELECT_ONE_FIELD_BY_KEY = "SELECT `key`, `value`, `creation_date` FROM fields WHERE `key` = %s"
COUNT_FIELDS_BY_KEY = "SELECT COUNT(*) FROM fields WHERE `key` = %s"
INSERT_FIELD = "INSERT INTO fields (`key`, value) VALUES (%s, %s)"
DELETE_FIELD_BY_KEY = "DELETE FROM fields WHERE `key` = %s"
# Users
SELECT_ALL_USERS = "SELECT username, email_phone, creation_date FROM users"
SELECT_ONE_USER_BY_ID = "SELECT username, email_phone, creation_date FROM users WHERE id = %s"
SELECT_ONE_USER_BY_USERNAME = "SELECT username, email_phone, creation_date FROM users WHERE `username` = %s"
COUNT_USERS_BY_USERNAME = "SELECT COUNT(*) FROM users WHERE username = %s"
INSERT_USER = "INSERT INTO users (username, email_phone) VALUES (%s, %s)"
DELETE_USER_BY_USERNAME = "DELETE FROM users WHERE username = %s"