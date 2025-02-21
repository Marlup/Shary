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

def build_email_string_body(sender, recipients, subject, filename, file_format, table_data, rows):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart()

    # Build the file as string
    if file_format == "json_req":
        file_to_send = get_selected_fields_as_req_json(table_data, rows, sender)
    else:
        file_to_send = build_file_from_selected_fields(table_data, rows, file_format)
    
    if file_to_send is None:
        return "bad-format"
    
    # Build the body and the hyperlink using HTML
    # shary_uri = "shary://files/open?filename=file_path.json"
    message_keys = parsed_table_as_vertical_string(table_data, rows)
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

def build_email_html_body(sender, recipients, subject, filename, file_format, table_data, rows):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart()

    # Build the file as string
    if file_format == "json_req":
        file_to_send = get_selected_fields_as_req_json(table_data, rows, sender)
    else:
        file_to_send = build_file_from_selected_fields(table_data, rows, file_format)
    
    if file_to_send is None:
        return "bad-format"
    
    # Build the body and the hyperlink using HTML
    # shary_uri = "shary://files/open?filename=file_path.json"
    message_keys = parsed_table_as_vertical_string(table_data, rows)
    shary_uri = f"http://localhost:5001/files/open?filename=./{filename}"
    body = f"""
<html>
<body>
    <p><a href="{shary_uri}" target="_blank">Open in Shary to visualize the data</a></p>
</body>
</html>
"""

    # Create the email
    #msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    #msg.set_content(MIMEText(body, "html"))
    #msg.add_attachment(file_to_send, filename=filename, subtype=file_format)

    return msg

def send_email(sender_email, sender_password, message):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        return ""
    except Exception as e:
        return e

def build_file_from_selected_fields(screen_table, rows, file_format="json"):
    if file_format == "json":
        return get_selected_fields_as_json(screen_table, rows)
    elif file_format == "csv":
        return get_selected_fields_as_csv(screen_table, rows)
    elif file_format == "xml":
        return get_selected_fields_as_xml(screen_table, rows)
    elif file_format == "yaml":
        return get_selected_fields_as_yaml(screen_table, rows)
    else:
        return None

def get_selected_fields_as_json(screen_table, rows):
    """ Get selected fields as a JSON dictionary. """
    json_fields = {}
    
    for row in rows:
        key = screen_table.item(row, 0).text().strip()
        value = screen_table.item(row, 1).text().strip()
        json_fields[key] = value
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_req_json(screen_table, rows, sender):
    """ Get fields as a JSON with request format. """
    json_fields = {}
    
    for row in rows:
        key = screen_table.item(row, 0).text().strip()
        value = screen_table.item(row, 1).text().strip()
        json_fields[key] = value
    json_fields["mode"] = "request"
    json_fields["sender"] = sender
    
    return json.dumps(json_fields, indent=4)

def get_selected_fields_as_xml(screen_table, rows):
    """ Get selected fields as an XML string. """
    root = ET.Element("Fields")

    for row in rows:
        key = screen_table.item(row, 0).text().strip()
        value = screen_table.item(row, 1).text().strip()

        field_element = ET.SubElement(root, "Field", key=key)
        field_element.text = value

    return ET.tostring(root, encoding="utf-8").decode("utf-8")

def get_selected_fields_as_csv(screen_table, rows):
    """ Get selected fields as a CSV string. """
    output = StringIO()
    writer = csv.writer(output)
    
    # Writing header
    writer.writerow(["Key", "Value"])

    for row in rows:
        key = screen_table.item(row, 0).text().strip()
        value = screen_table.item(row, 1).text().strip()
        writer.writerow([key, value])

    return output.getvalue()

def get_selected_fields_as_yaml(screen_table, rows):
    """ Get selected fields as a YAML dictionary. """
    yaml_fields = {}
    
    for row in rows:
        key = screen_table.item(row, 0).text().strip()
        value = screen_table.item(row, 1).text().strip()
        yaml_fields[key] = value

    return yaml.dump(yaml_fields, 
                     default_flow_style=False,
                     allow_unicode=True)

def parsed_table_as_vertical_string(screen_table, rows):
    keys_values = []
    for row in rows:
        k = screen_table.item(row, 0).text().strip()
        v = screen_table.item(row, 1).text().strip()
        keys_values.append(f"- {k}: {v}")
    
    parsed_json = "\n\t" + "\n\t".join(keys_values)
    return parsed_json