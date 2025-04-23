import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fpdf import FPDF
from datetime import datetime
import os

def create_certificate_pdf(user_email, skill_name, date=None):
    """Create a PDF certificate using FPDF."""
    # Initialize PDF
    pdf = FPDF(orientation='L', format='A4')
    pdf.add_page()
    
    # Set background color
    pdf.set_fill_color(251, 247, 240)  # Cream color background
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    # Add border
    pdf.set_line_width(2)
    pdf.rect(10, 10, pdf.w - 20, pdf.h - 20)
    
    # Add organization name
    pdf.set_font('Times', 'B', 28)
    pdf.cell(0, 30, 'OLL', 0, 1, 'C')
    
    # Add "CERTIFICATE" text
    pdf.set_font('Times', 'B', 50)
    pdf.set_text_color(139, 101, 77)  # Brown color
    pdf.cell(0, 40, 'CERTIFICATE', 0, 1, 'C')
    
    # Add recipient email
    pdf.set_font('Times', '', 24)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 30, user_email, 0, 1, 'C')
    
    # Add "has successfully completed"
    pdf.set_font('Times', '', 16)
    pdf.cell(0, 15, 'has successfully completed', 0, 1, 'C')
    
    # Add skill name
    pdf.set_font('Times', 'B', 32)
    pdf.set_text_color(139, 101, 77)  # Brown color
    pdf.cell(0, 25, skill_name, 0, 1, 'C')
    
    # Add date and signature
    pdf.set_font('Times', '', 16)
    pdf.set_text_color(0, 0, 0)
    
    # Date on left
    date_str = date if date else datetime.now().strftime("%dth %B %Y")
    pdf.line(70, pdf.get_y() + 30, 150, pdf.get_y() + 30)  # Line for date
    pdf.text(90, pdf.get_y() + 40, 'Date')
    pdf.text(70, pdf.get_y() + 25, date_str)
    
    # Signature on right
    pdf.line(pdf.w - 150, pdf.get_y() + 30, pdf.w - 70, pdf.get_y() + 30)  # Line for signature
    pdf.text(pdf.w - 120, pdf.get_y() + 40, 'President')
    pdf.text(pdf.w - 140, pdf.get_y() + 25, 'Dr. Seema Negi')
    
    # Save to a temporary file
    temp_path = f'certificate_{user_email.replace("@", "_at_")}.pdf'
    pdf.output(temp_path)
    return temp_path

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
        
        # Add PDF attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                message.attach(pdf_attachment)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        
        # Clean up temporary file
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
            
        return True
    except Exception as e:
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
        raise Exception(f"Error sending email: {str(e)}")

def send_certificate(email, skill_name, date=None):
    """Send certification email with PDF certificate to user."""
    # Create the PDF certificate
    pdf_path = create_certificate_pdf(email, skill_name, date)
    
    # Prepare email body
    body = f"""Congratulations!

We are pleased to inform you that you have successfully completed the certification for {skill_name}.

Your certificate is attached to this email. 

Best regards,
OLL.co"""

    # Send email with PDF attachment
    subject = "Your Certification for {skill_name}"
    send_email(email, subject, body, pdf_path)

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