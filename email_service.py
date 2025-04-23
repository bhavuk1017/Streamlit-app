import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

def send_email(to_email, subject, body, attachment_path=None):
    """Send email using Gmail API with optional PDF attachment."""
    try:
        creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.send"])
        service = build("gmail", "v1", credentials=creds)
        
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        
        # Add body
        message.attach(MIMEText(body))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                message.attach(attachment)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        
        # Clean up temporary file if it exists
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
            
        return True
    except Exception as e:
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
        raise Exception(f"Error sending email: {str(e)}")

def send_certificate(email, task_description, certificate_content):
    """Send certification email to user."""
    subject = "Certification Achieved!"
    send_email(email, subject, certificate_content)

def send_evaluation_result(email, evaluation_result):
    """Send evaluation results to invigilator."""
    subject = "Evaluation Results"
    send_email(email, subject, evaluation_result)

def send_task_details(email, task_details):
    """Send task details to user."""
    subject = "Your Certification Task"
    send_email(email, subject, task_details)

def send_observation_sheet(email, obs_sheet):
    """Send observation sheet to invigilator."""
    subject = "Observation Sheet"
    send_email(email, subject, obs_sheet)