import os
import json
import json
import csv
import yaml
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any

import keyring
from flask import Flask, request, jsonify
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from core.constant import (

    FIREBASE_HOST,
    FIREBASE_PORT,
    PATH_ENV_VARIABLES
)

from core.dtos import OwnerDTO

FIREBASE_ENDPOINT = f"http://{FIREBASE_HOST}:{FIREBASE_PORT}/shary-21b61/us-central1"

def restrict_access():
    allowed_ips = ['127.0.0.1']
    if request.remote_addr not in allowed_ips:
        return jsonify({"error": "Access forbidden"}), 403

def open_file():
    filename = request.args.get("filename")
    if filename:
        return jsonify({"message": f"Processing {filename}..."}), 200
    else:
        return jsonify({"error": "No filename provided."}), 400

def run_flask():
    backend_app = Flask(__name__)
    backend_app.before_request(restrict_access)
    backend_app.add_url_rule("/files/open", "open_file", open_file, methods=['GET'])
    backend_app.run(host="127.0.0.1", port=5000)

def is_dir_empty(path):
    return os.path.isdir(path) and len(os.listdir(path)) == 0

def load_user_credentials():
    sender_email = keyring.get_password("shary_app", "owner_email")  # Replace with your email
    sender_password = "ugtt iggn nnni dchj"  # Replace with your app password
    
    return sender_email, sender_password

def build_file_from_selected_fields(rows, file_format="json") -> (str | dict | Any | None):
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

def get_selected_fields_as_req_json(rows, sender, as_dict=False) -> (str | dict):
    """ Get fields as a JSON with request format. """
    json_fields = {"keys": []}
    
    for key, *_ in rows:
        json_fields["keys"].append(key)
    
    json_fields["mode"] = "request"
    json_fields["sender"] = sender
    
    if as_dict:
        return json_fields
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_csv(rows) -> Any:
    """ Get selected fields as a CSV string. """
    output = StringIO()
    writer = csv.writer(output)
    
    # Writing header
    writer.writerow(["Key", "Value"])

    for key, value, *_ in rows:
        writer.writerow([key, value])

    return output.getvalue()

def get_selected_fields_as_xml(rows) -> str:
    """ Get selected fields as an XML string. """
    root = ET.Element("Fields")

    for key, value, *_ in rows:
        field_element = ET.SubElement(root, "Field", key=key)
        field_element.text = value

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

def get_selected_fields_as_yaml(rows) -> str:
    """ Get selected fields as a YAML dictionary. """
    yaml_fields = {}
    
    for key, value, *_ in rows:
        yaml_fields[key] = value

    return yaml.dump(yaml_fields, 
                     default_flow_style=False,
                     allow_unicode=True)

def parsed_fields_as_vertical_string(rows) -> str:
    keys_values = []
    for key, value, *_ in rows:
        keys_values.append(f"- {key}: {value}")
    
    parsed_json = "\n\t" + "\n\t".join(keys_values)
    return parsed_json

def parsed_keys_as_vertical_string(rows) -> str:
    keys = []
    for key, *_ in rows:
        keys.append(f"- {key}")
    
    parsed_json = "\n\t" + "\n\t".join(keys)
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
                added_date TEXT DEFAULT (DATE('now'))
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
                added_date TEXT DEFAULT (DATE('now'))
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
                added_date TEXT DEFAULT (DATE('now'))
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

def get_checked_rows(table, checked_rows) -> list:
    """Returns the manually tracked checked rows."""
    if table is None or not checked_rows:
        return []
    return checked_rows