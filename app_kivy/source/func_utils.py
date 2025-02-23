import os
from dotenv import load_dotenv
import smtplib
import json
from email.message import EmailMessage
import xml.etree.ElementTree as ET
import csv
import yaml
from io import StringIO

def load_user_credentials():
    load_dotenv("../.env")
    sender_email = os.getenv("SHARY_USER_EMAIL")  # Replace with your email
    sender_password = "ugtt iggn nnni dchj"  # Replace with your app password
    
    return sender_email, sender_password

def build_email_string_body(sender, recipients, subject, filename, file_format, rows):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart()

    # Build the file as string
    if file_format == "json_req":
        file_to_send = get_selected_fields_as_req_json(rows, sender)
    else:
        file_to_send = build_file_from_selected_fields(rows, file_format)
    
    if file_to_send is None:
        return "bad-format"
    
    # Build the body and the hyperlink using HTML
    # shary_uri = "shary://files/open?filename=file_path.json"
    message_keys = parsed_table_as_vertical_string(rows)
    shary_uri = f"http://files/open?filename=./{filename}"

    body = (
        "Hello,\n\n"
        "You are receiving this email from Shary.\n"
        "Shary is an application that allows users to share structured data easily.\n\n"
        f"{shary_uri}"
        "Fields:\n"
        f"{message_keys}"
        "\n\nBest regards,\nShary Team"
    )
    
    # Create the email
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(MIMEText(body, "html"))
    msg.add_attachment(file_to_send, filename=filename, subtype=file_format)
    return msg

def build_email_html_body(sender, recipients, subject, filename, file_format, rows):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Build the file as string
    print(f"file_format : {file_format}")
    if file_format == "json_req":
        file_to_send = get_selected_fields_as_req_json(rows, sender)
    else:
        file_to_send = build_file_from_selected_fields(rows, file_format)
    
    if file_to_send is None:
        return "bad-format"
    
    # Build the body and the hyperlink using HTML
    # shary_uri = "shary://files/open?filename=file_path.json"
    message_keys = parsed_table_as_vertical_string(rows)
    shary_uri = f"http://localhost:5001/files/open?filename=./{filename}"
    body = f"""
<html>
<body>
    <p>
        <a href="{shary_uri}" target="_blank">Click to open Shary and visualize the data</a>
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
    
    for row in rows:
        key, value = row.field_data
        json_fields[key] = value
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_req_json(rows, sender):
    """ Get fields as a JSON with request format. """
    json_fields = {}
    
    for row in rows:
        key, value = row.field_data
        json_fields[key] = value
    json_fields["mode"] = "request"
    json_fields["sender"] = sender
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_xml(rows):
    """ Get selected fields as an XML string. """
    root = ET.Element("Fields")

    for row in rows:
        key, value = row.field_data
        field_element = ET.SubElement(root, "Field", key=key)
        field_element.text = value

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

def get_selected_fields_as_csv(rows):
    """ Get selected fields as a CSV string. """
    output = StringIO()
    writer = csv.writer(output)
    
    # Writing header
    writer.writerow(["Key", "Value"])

    for row in rows:
        key, value = row.field_data
        writer.writerow([key, value])

    return output.getvalue()

def get_selected_fields_as_yaml(rows):
    """ Get selected fields as a YAML dictionary. """
    yaml_fields = {}
    
    for row in rows:
        key, value = row.field_data
        yaml_fields[key] = value

    return yaml.dump(yaml_fields, 
                     default_flow_style=False,
                     allow_unicode=True)

def parsed_table_as_vertical_string(rows):
    keys_values = []
    for row in rows:
        key, value = row.field_data
        keys_values.append(f"- {key}: {value}")
    
    parsed_json = "\n\t" + "\n\t".join(keys_values)
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

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.lang.builder import Builder

def build_success_dialog():
    return Builder.load_string('''
BoxLayout:
  orientation: 'vertical'
  MDRaisedButton:
    text: "Email Success"
    on_release: app.show_success_dialog()
                               '''
                               )

def show_success_dialog():
    dialog = MDDialog(
        title="Success",
        text="Fields sent successfully!",
        buttons=[
            MDRaisedButton(
                text="OK",
                on_release=lambda x: dialog.dismiss()
            ),
        ],
    )
    dialog.open()

# Warnings
def build_no_fields_warning_dialog():
    return Builder.load_string('''
BoxLayout:
  orientation: 'vertical'
  MDRaisedButton:
    text: "No Fields Selected"
    on_release: app.show_no_fields_warning_dialog()
                               '''
                               )

def show_no_fields_warning_dialog():
    dialog = MDDialog(
        title="Warning",
        text="Please select at least one field to send.",
        buttons=[
            MDRaisedButton(
                text="OK",
                on_release=lambda x: dialog.dismiss()
            ),
        ],
    )
    dialog.open()

def build_format_warning_dialog():
    return Builder.load_string('''
BoxLayout:
  orientation: 'vertical'
  MDRaisedButton:
    text: "Bad Format"
    on_release: app.show_format_warning_dialog()
                               '''
                               )

def show_format_warning_dialog():
    dialog = MDDialog(
        title="Warning",
        text="Unsupported format.",
        buttons=[
            MDRaisedButton(
                text="OK",
                on_release=lambda x: dialog.dismiss()
            ),
        ],
    )
    dialog.open()

# Errors
def build_email_error_dialog():
    return Builder.load_string('''
BoxLayout:
  orientation: 'vertical'
  MDRaisedButton:
    text: "Email Error"
    on_release: app.show_email_error_dialog()
                               '''
                               )

def show_email_error_dialog():
    dialog = MDDialog(
        title="Error at email send",
        text="Unsupported format.",
        buttons=[
            MDRaisedButton(
                text="OK",
                on_release=lambda x: dialog.dismiss()
            ),
        ],
    )
    dialog.open()