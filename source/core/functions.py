import os
import sys
import re
import json
import csv
import yaml
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any
import logging

import keyring
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from core.constant import (
    BACKEND_HOST,
    BACKEND_PORT,
    PATH_DATA_DOWNLOAD
)

BACKEND_ENDPOINT = f"http://{BACKEND_HOST}:{BACKEND_PORT}/shary-21b61/us-central1"


def resource_path(relative_path):
    """ Get absolute path to resource (handles PyInstaller build and dev run) """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_dir_empty(path: str):
    return os.path.isdir(path) and len(os.listdir(path)) == 0

def load_user_credentials():
    sender_email = keyring.get_password("shary_app", "owner_email")  # Replace with your email
    sender_password = "ugtt iggn nnni dchj"  # Replace with your app password
    
    return sender_email, sender_password

def load_file_of_fields(filename):
    path_current_file = os.path.join(PATH_DATA_DOWNLOAD, filename)
    with open(path_current_file, "r") as f:
        return json.load(f)

def build_file_from_selected_fields(
        rows: list[str], 
        file_format: str="json"
        ) -> (str | dict[str, str] | Any | None):
    if file_format == "json":
        return get_selected_fields_as_json(rows)
    elif file_format == "csv":
        return get_selected_fields_as_csv(rows)
    elif file_format == "xml":
        return get_selected_fields_as_xml(rows)
    elif file_format == "yaml":
        return get_selected_fields_as_yaml(rows)
    else:
        return None

def get_selected_fields_as_json(rows, as_dict=False) -> (str | dict):
    """ Get selected fields as a JSON dictionary. """
    json_fields = {}
    
    for key, value, *_ in rows:
        json_fields[key] = value
    
    if as_dict:
        return json_fields
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_req_json(rows: list[str], sender: str, as_dict=False) -> (str | dict[str, str]):
    """ Get fields as a JSON with request format. """
    json_fields = {"keys": []}
    
    for key, *_ in rows:
        json_fields["keys"].append(key)
    
    json_fields["mode"] = "request"
    json_fields["sender"] = sender
    
    if as_dict:
        return json_fields
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_csv(rows: list[str]) -> Any:
    """ Get selected fields as a CSV string. """
    output = StringIO()
    writer = csv.writer(output)
    
    # Writing header
    writer.writerow(["Key", "Value"])

    for key, value, *_ in rows:
        writer.writerow([key, value])

    return output.getvalue()

def get_selected_fields_as_xml(rows: list[str]) -> str:
    """ Get selected fields as an XML string. """
    root = ET.Element("Fields")

    for key, value, *_ in rows:
        field_element = ET.SubElement(root, "Field", key=key)
        field_element.text = value

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

def get_selected_fields_as_yaml(rows: list[str]) -> str:
    """ Get selected fields as a YAML dictionary. """
    yaml_fields = {}
    
    for key, value, *_ in rows:
        yaml_fields[key] = value

    return yaml.dump(yaml_fields, 
                     default_flow_style=False,
                     allow_unicode=True)

def parsed_fields_as_vertical_string(rows: list[str]) -> str:
    keys_values = []
    for key, value, *_ in rows:
        keys_values.append(f"· {key}: {value}\n\t")
    
    return "".join(keys_values)

def parsed_keys_as_vertical_string(rows) -> str:
    keys = []
    for key, *_ in rows:
        keys.append(f"\n\t· {key}")
    
    parsed_json = "".join(keys)
    return parsed_json

def try_make_base_tables(conn=None):
    if conn is None:
        from sqlite3 import Connection
        
        conn = Connection("shary_demo.db")
        conn.cursor()
        # dates are ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS").

        # Create fields table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(256) UNIQUE NOT NULL,
                value TEXT,
                alias_key VARCHAR(256),
                date_added TEXT DEFAULT (DATE('now'))
            );
            """
            )
        # Create users table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(256) NOT NULL,
                email VARCHAR(256) UNIQUE NOT NULL,
                phone_number INTEGER,
                phone_extension INTEGER,
                date_added TEXT DEFAULT (DATE('now'))
            );
            """
            )
        # Create requests table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receivers VARCHAR NOT NULL,
                keys VARCHAR NOT NULL,
                date_added TEXT DEFAULT (DATE('now'))
            );
            """
            )
            
        conn.commit()
        conn.close()

def information_panel(panel_name, message):
    return_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

    # Message label
    message_label = Label(text=message, halign="center", valign="middle")
    # Bind the label size to its text_size so the text is centered properly
    message_label.bind(size=message_label.setter("text_size"))

    # Message ok button
    message_ok_button = Button(text="Ok", 
                                on_press=lambda _: message_popup.dismiss(),
                                size_hint=(None, None),
                                size=(100, 44), 
                                halign="center"
                                )
    
    # Add widgets
    return_layout.add_widget(message_label)
    return_layout.add_widget(message_ok_button)

    # Message popup
    message_popup = Popup(title=panel_name, content=return_layout, size_hint=(0.5, 0.4))
    message_popup.open()

def check_new_json_files(old_files) -> bool:
    n_new_files = len(os.listdir(PATH_DATA_DOWNLOAD))
    if old_files and len(old_files) == n_new_files:
        return False
    return True

def get_json_files() -> list[str]:
    """Retrieve available JSON files from a directory."""
    if not os.path.exists(PATH_DATA_DOWNLOAD):
        os.makedirs(PATH_DATA_DOWNLOAD)
    
    downloaded_files = os.listdir(PATH_DATA_DOWNLOAD)
    return [f for f in downloaded_files if f.endswith(".json")]

def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (!@#$%^&*...)."
    
    logging.debug("Password syntax validated")
    return True, ""

def validate_email_syntax(email: str) -> str | None:
    if not email:
        return False, "Email cannot be empty."
    if not "@" in email:
        return False, "Unexpected email format: @?."
    if email.startswith("@"):
        return False, "Unexpected email format: starts with @."
    
    logging.debug(f"Email syntax validated: '{email}'")
    return True, ""
    
    #re.search("^\w+@\w[.]{1}\w")

def enter_message(has_creds: bool, is_registered: bool):
    if has_creds:
        msg_creds = "You have credentials."
    else:
        msg_creds = "You don't have credentials"
    if is_registered:
        msg_regis = "You are registered and online"
    else:  
        msg_regis = "You are not registered or online"
    
    return f"{msg_creds} {msg_regis}"