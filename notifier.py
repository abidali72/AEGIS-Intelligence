import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class AegisNotifier:
    """
    Aegis Neural Alert System (v6.0)
    Handles SMTP transmission of security incidents with image attachments.
    """
    def __init__(self):
        # Configuration - USER SHOULD UPDATE THESE
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender_email = "your-email@gmail.com" # Update with sender email
        self.app_password = "your-app-password"    # Update with Google App Password
        self.receiver_email = "ibnemurad032@gmail.com"
        
        self.is_configured = False # Set to True only after user adds credentials

    def send_alert(self, image_path, event_type, product):
        if not self.is_configured:
            print("[Aegis Notifier] Skipping email: SMTP not configured.")
            return False

        try:
            # Create a multipart message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.receiver_email
            message["Subject"] = f"🚨 SECURITY ALERT: {event_type} Detected"

            # Create body
            body = f"""
            AEGIS INTELLIGENCE ENGINE - SECURITY REPORT
            -------------------------------------------
            Event: {event_type}
            Product identified: {product}
            Status: Critical Alert Triggered
            
            Please see the attached capture for visual confirmation.
            
            -- Aegis Intelligence v6.0
            """
            message.attach(MIMEText(body, "plain"))

            # Attach Image
            if os.path.exists(image_path):
                with open(image_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(image_path)}",
                    )
                    message.attach(part)

            # Connect and Send
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            
            print(f"[Aegis Notifier] Alert successfully transmitted to {self.receiver_email}")
            return True

        except Exception as e:
            print(f"[Aegis Notifier] Failed to transmit alert: {e}")
            return False

# Setup Instructions for User:
# 1. Enable 2-Step Verification on your Google Account.
# 2. Go to Security > App Passwords.
# 3. Generate a password for 'Mail' and 'Windows Computer'.
# 4. Copy the 16-character code into the 'app_password' field above.
# 5. Set 'is_configured' to True.
