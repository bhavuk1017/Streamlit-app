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
        
        # Create message container
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        
        # Add body
        message.attach(MIMEText(body))
        
        # Add PDF attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                pdf = MIMEApplication(f.read(), _subtype="pdf")
                pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                message.attach(pdf)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return True
    except Exception as e:
        raise Exception(f"Error sending email: {str(e)}")

def send_certificate(email, task_description, certificate_path):
    """Send certification email with PDF certificate to user."""
    subject = "Certification Achieved!"
    body = f"""Congratulations!

We are pleased to inform you that you have successfully completed your certification.
Your certificate is attached to this email.

Best regards,
Skill Bharat Association"""
    
    send_email(email, subject, body, certificate_path)

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