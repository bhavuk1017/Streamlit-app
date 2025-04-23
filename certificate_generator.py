from fpdf import FPDF
import os
from datetime import datetime
import pytz

def generate_certificate_pdf(email, skill, message):
    """Generate a PDF certificate using FPDF."""
    # Create PDF object
    pdf = FPDF(orientation='L', format='A4')
    pdf.add_page()
    
    # Set default font - using built-in fonts instead of custom ones
    pdf.set_font('Helvetica', '', 36)
    
    # Certificate border
    pdf.set_line_width(2)
    pdf.rect(10, 10, pdf.w - 20, pdf.h - 20)
    pdf.rect(15, 15, pdf.w - 30, pdf.h - 30)
    
    # Title
    pdf.set_font('Helvetica-Bold', '', 36)
    pdf.cell(0, 40, 'OLL.co', 0, 1, 'C')
    
    # Certificate text
    pdf.set_font('Helvetica-Bold', '', 48)
    pdf.cell(0, 30, 'CERTIFICATE', 0, 1, 'C')
    
    # Email
    pdf.set_font('Helvetica', '', 16)
    pdf.cell(0, 20, email, 0, 1, 'C')
    
    # Has successfully completed text
    pdf.set_font('Helvetica', '', 16)
    pdf.cell(0, 10, 'has successfully completed', 0, 1, 'C')
    
    # Skill name
    pdf.set_font('Helvetica-Bold', '', 24)
    pdf.cell(0, 20, skill, 0, 1, 'C')
    
    # Message
    if message:
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 10, message, 0, 1, 'C')
    
    # Date
    current_date = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%dth %B %Y')
    pdf.set_font('Helvetica', '', 14)
    pdf.cell(pdf.w/2 - 20, 40, current_date, 0, 0, 'C')
    
    # Signature
    pdf.cell(pdf.w/2 + 20, 40, 'Dr. Seema Negi', 0, 1, 'C')
    
    # Labels for date and signature
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(pdf.w/2 - 20, 0, 'Date', 0, 0, 'C')
    pdf.cell(pdf.w/2 + 20, 0, 'President', 0, 1, 'C')
    
    # Save to a temporary file
    temp_path = f"temp_certificate_{email.replace('@', '_').replace('.', '_')}.pdf"
    pdf.output(temp_path)
    
    return temp_path 