import os
import smtplib
from email.message import EmailMessage

from core.session import CurrentSession

from core.constant import (
    MSG_DEFAULT_SEND_FILENAME,
    SMTP_SERVER,
    SMTP_SSL_PORT,
    FILE_FORMATS,
    PATH_ENV_VARIABLES
)

from core.functions import (
    parsed_fields_as_vertical_string,
    parsed_keys_as_vertical_string,
    get_selected_fields_as_req_json,
    build_file_from_selected_fields,
    information_panel
)

class EmailService():
    def __init__(self):
        self.session: CurrentSession = CurrentSession.get_instance()
        self.email = self.session.email
        self.username = self.session.username
        self.email_password = "ugtt iggn nnni dchj"  # Replace with a safer secret handling strategy

    def _send(self, message):
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_SSL_PORT) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            information_panel("Action: sending email", "Email sent successfully")
        except Exception as e:
            information_panel("Action: sending email", f"Error at sending: {str(e)}")
        
    def create_payload(self, rows, recipients, filename, file_format) -> dict | None:
            if not rows:
                information_panel("Action: sending email", "No fields selected.")
                return None

            if not recipients:
                information_panel("Action: sending email", "Select at least one external user.")
                return None

            if file_format not in FILE_FORMATS:
                information_panel("Action: sending email", "Invalid file format.")
                return None

            subject = f"Shary message with {len(rows)} fields"

            return {
                "sender_email": self.sender_email,
                "sender_password": self.sender_password,
                "recipients": recipients,
                "subject": subject,
                "rows": rows,
                "filename": filename,
                "file_format": file_format
            }

    def send_from_payload(self, payload: dict):
        message = self._build_email(
            payload["sender_email"],
            payload["recipients"],
            payload["subject"],
            payload["rows"],
            payload["filename"],
            payload["file_format"]
        )
        self._send(payload["sender_email"], payload["sender_password"], message)

    def _build_email(self, recipients, subject, rows_to_send, filename=None, file_format="json"):
        if not filename:
            filename = f"{MSG_DEFAULT_SEND_FILENAME}{self.sender_name}"
        filename += f".{file_format}"
        return self._build_email_html_body(
            recipients,
            subject,
            filename,
            file_format,
            rows_to_send
        )

    def _build_email_html_body(self, recipients, subject, filename, file_format, rows, on_request=False):
        if on_request:
            message_keys = parsed_keys_as_vertical_string(rows)
            file_to_send = get_selected_fields_as_req_json(rows, self.sender_email)
        else:
            message_keys = parsed_fields_as_vertical_string(rows)
            file_to_send = build_file_from_selected_fields(rows, file_format)

        if file_to_send is None:
            return "bad-format"

        shary_uri = f"http://localhost:5001/files/open?filename=./{filename}"
        body = f"""
        <html>
        <body>
            <p>Hello,<br><br>
            You are receiving this email from Shary.<br><br>
            {shary_uri}<br><br>
            Fields:<br>
            {message_keys}<br><br>
            <a href="{shary_uri}" target="_blank">Click to open Shary and visualize the data</a><br><br>
            Best regards,<br>Shary Team
            </p>
        </body>
        </html>
        """
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body, "html")
        msg.add_attachment(file_to_send, filename=filename, subtype=file_format)
        return msg
