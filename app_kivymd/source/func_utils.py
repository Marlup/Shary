import os
from dotenv import load_dotenv
import smtplib
import json
from email.message import EmailMessage
import xml.etree.ElementTree as ET
import csv
import yaml
from io import StringIO

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

def load_user_credentials():
    load_dotenv("../.env")
    sender_email = os.getenv("SHARY_ROOT_EMAIL")  # Replace with your email
    sender_password = "ugtt iggn nnni dchj"  # Replace with your app password
    
    return sender_email, sender_password

def build_email_html_body(sender, recipients, subject, filename, file_format, rows, on_request=False):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Build the file as string
    if on_request:
        message_keys = parsed_keys_as_vertical_string(rows)
        file_to_send = get_selected_fields_as_req_json(rows, sender)
    else:
        message_keys = parsed_fields_as_vertical_string(rows)
        file_to_send = build_file_from_selected_fields(rows, file_format)
    
    if file_to_send is None:
        return "bad-format"
    
    # Build the body and the hyperlink using HTML
    # shary_uri = "shary://files/open?filename=file_path.json"
    shary_uri = f"http://localhost:5001/files/open?filename=./{filename}"
    body = f"""
<html>
<body>
    <p>
        Hello,

        You are receiving this email from Shary.\n
        Shary is an application that allows users to share structured data easily.\n\n
        {shary_uri}

        Fields:\n
        {message_keys}

        <a href="{shary_uri}" target="_blank">Click to open Shary and visualize the data</a>

        \n\nBest regards,\nShary Team
    </p>
</body>
</html>
"""
    # Create the email
    #msg = MIMEMultipart()
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))
    #msg.set_content(body, "html")
    #msg.set_content(MIMEText(body, "html"))
    #msg.add_alternative(body, subtype="html")
    msg.add_attachment(file_to_send, filename=filename, subtype=file_format)

    return msg

def send_email(sender_email, sender_password, message):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("")
        return ""
    except Exception as e:
        return e

def build_file_from_selected_fields(rows, file_format="json"):
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

def get_selected_fields_as_json(rows):
    """ Get selected fields as a JSON dictionary. """
    json_fields = {}
    
    for key, value, *_ in rows:
        json_fields[key] = value
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_req_json(rows, sender):
    """ Get fields as a JSON with request format. """
    json_fields = {"keys": []}
    
    for key, *_ in rows:
        json_fields["keys"].append(key)
    
    json_fields["mode"] = "request"
    json_fields["sender"] = sender
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_xml(rows):
    """ Get selected fields as an XML string. """
    root = ET.Element("Fields")

    for key, value, *_ in rows:
        field_element = ET.SubElement(root, "Field", key=key)
        field_element.text = value

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

def get_selected_fields_as_csv(rows):
    """ Get selected fields as a CSV string. """
    output = StringIO()
    writer = csv.writer(output)
    
    # Writing header
    writer.writerow(["Key", "Value"])

    for key, value, *_ in rows:
        writer.writerow([key, value])

    return output.getvalue()

def get_selected_fields_as_yaml(rows):
    """ Get selected fields as a YAML dictionary. """
    yaml_fields = {}
    
    for key, value, *_ in rows:
        yaml_fields[key] = value

    return yaml.dump(yaml_fields, 
                     default_flow_style=False,
                     allow_unicode=True)

def parsed_fields_as_vertical_string(rows):
    keys_values = []
    for key, value, *_ in rows:
        keys_values.append(f"- {key}: {value}")
    
    parsed_json = "\n\t" + "\n\t".join(keys_values)
    return parsed_json

def parsed_keys_as_vertical_string(rows):
    keys = []
    for key, *_ in rows:
        keys.append(f"- {key}")
    
    parsed_json = "\n\t" + "\n\t".join(keys)
    return parsed_json

def make_base_tables(conn=None):
    if conn is None:
        from sqlite3 import Connection
        
        conn = Connection("shary_demo")
        conn.cursor()
        # dates are ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS").
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(256) UNIQUE NOT NULL,
                value TEXT,
                custom_name VARCHAR(256),
                creation_date TEXT DEFAULT (DATE('now'))
            );
            """
            )
        
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(256) NOT NULL,
                email VARCHAR(256) UNIQUE NOT NULL,
                phone_number INTEGER,
                phone_extension INTEGER,
                creation_date TEXT DEFAULT (DATE('now'))
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