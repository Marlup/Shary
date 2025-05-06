import smtplib
from email.message import EmailMessage

from core.session import Session

from core.constant import (
    MSG_DEFAULT_SEND_FILENAME,
    SMTP_SERVER,
    SMTP_SSL_PORT,
    FILE_FORMATS,
)

from core.functions import (
    parsed_fields_as_vertical_string,
    parsed_keys_as_vertical_string,
    get_selected_fields_as_req_json,
    build_file_from_selected_fields,
    information_panel
)


class EmailService():
    def __init__(self, session: Session):
        self.session = session
        self.email_password = "ugtt iggn nnni dchj"  # Replace with a safer secret handling strategy

    def _send(self, message):
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_SSL_PORT) as server:
                server.login(self.session.get_email(), self.email_password)
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
                "sender_email": self.session.get_email(),
                "sender_password": self.email_password,
                "recipients": recipients,
                "subject": subject,
                "rows": rows,
                "filename": filename,
                "file_format": file_format
            }

    def send_from_payload(self, payload: dict):
        message = self._build_email(
            payload["recipients"],
            payload["subject"],
            payload["rows"],
            payload["filename"],
            payload["file_format"]
        )
        self._send(message)

    def _build_email(self, recipients, subject, rows_to_send, filename=None, file_format="json"):
        if not filename:
            filename = f"{MSG_DEFAULT_SEND_FILENAME}{self.session.username}"
        
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
            file_to_send = get_selected_fields_as_req_json(rows, self.session.get_email())
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
            This email was sent from a Shary service.<br><br>
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
        msg["From"] = self.session.get_email()
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body, "html")
        msg.add_attachment(file_to_send, filename=filename, subtype=file_format)
        return msg

    def send_email_with_fields(self, rows, recipients, filename, file_format: str="json"):
        payload = self.create_payload(rows, recipients, filename, file_format)
        if payload:
            self.send_from_payload(payload)