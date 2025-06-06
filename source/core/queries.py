# Fields
SELECT_ALL_FIELDS = "SELECT `key`, `value`, alias_key, `date_added` FROM fields"
SELECT_ONE_FIELD_BY_ID = "SELECT `key`, `value`, alias_key, `date_added` FROM fields WHERE `id` = ?"
SELECT_ONE_FIELD_BY_KEY = "SELECT `key`, `value`, alias_key, `date_added` FROM fields WHERE `key` = ?"
COUNT_FIELDS_BY_KEY = "SELECT COUNT(*) FROM fields WHERE `key` = ?"
INSERT_FIELD = "INSERT INTO fields (`key`, value, alias_key) VALUES (?, ?, ?)"
DELETE_FIELD_BY_KEY = "DELETE FROM fields WHERE `key` = ?"
# Users
SELECT_ALL_USERS = "SELECT username, email, date_added FROM users"
SELECT_ONE_USER_BY_ID = "SELECT username, email, date_added FROM users WHERE id = ?"
SELECT_ONE_USER_BY_USERNAME = "SELECT username, email, date_added FROM users WHERE `username` = ?"
COUNT_USERS_BY_USERNAME = "SELECT COUNT(*) FROM users WHERE username = ?"
INSERT_USER = "INSERT INTO users (username, email) VALUES (?, ?)"
DELETE_USER_BY_USERNAME = "DELETE FROM users WHERE username = ?"
# Requests
SELECT_ALL_REQUESTS = "SELECT receivers, keys, date_added FROM requests"
SELECT_ONE_REQUEST_BY_ID = "SELECT receivers, keys, date_added FROM requests WHERE id = ?"
SELECT_ONE_REQUEST_BY_RECEIVERS = "SELECT keys, date_added FROM requests WHERE `receivers` = ?"
COUNT_REQUESTS = "SELECT COUNT(*) FROM requests"
INSERT_REQUEST = "INSERT INTO requests (receivers, keys) VALUES (?, ?)"
DELETE_REQUEST_BY_RECEIVERS = "DELETE FROM requests WHERE receivers = ?"