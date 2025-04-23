from fpdf import FPDF
import os
from datetime import datetime
import pytz

class CertificateGenerator:
    def __init__(self):
        self.pdf = FPDF(orientation='L', format='A4')
        self.pdf.add_page()
        
    def generate_certificate(self, email, skill, message):
        # Set up the PDF
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add border
        self.pdf.set_line_width(1)
        self.pdf.set_draw_color(139, 69, 19)  # Brown color for border
        self.pdf.rect(10, 10, self.pdf.w - 20, self.pdf.h - 20)
        
        # Add header
        self.pdf.set_font('Arial', 'B', 32)
        self.pdf.set_text_color(139, 69, 19)  # Brown color for text
        self.pdf.cell(0, 30, 'OLL.co', 0, 1, 'C')
        
        # Add "CERTIFICATE" text
        self.pdf.set_font('Arial', 'B', 48)
        self.pdf.cell(0, 30, 'CERTIFICATE', 0, 1, 'C')
        
        # Add recipient email
        self.pdf.set_font('Arial', '', 16)
        self.pdf.set_text_color(0, 0, 0)  # Black color for text
        self.pdf.cell(0, 20, email, 0, 1, 'C')
        
        # Add "has successfully completed" text
        self.pdf.cell(0, 15, 'has successfully completed', 0, 1, 'C')
        
        # Add skill name
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.set_text_color(139, 69, 19)  # Brown color for text
        self.pdf.cell(0, 25, skill, 0, 1, 'C')
        
        # Add message if provided
        if message:
            self.pdf.set_font('Arial', '', 12)
            self.pdf.set_text_color(0, 0, 0)  # Black color for text
            self.pdf.cell(0, 15, message, 0, 1, 'C')
        
        # Add date
        current_date = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%dth %B %Y')
        self.pdf.set_font('Arial', '', 14)
        self.pdf.set_y(self.pdf.h - 50)
        self.pdf.cell(self.pdf.w/2 - 20, 10, current_date, 0, 0, 'C')
        
        # Add signature
        self.pdf.cell(self.pdf.w/2 + 20, 10, 'Dr. Seema Negi', 0, 1, 'C')
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(self.pdf.w/2 - 20, 10, 'Date', 0, 0, 'C')
        self.pdf.cell(self.pdf.w/2 + 20, 10, 'President', 0, 1, 'C')
        
        # Save the certificate
        certificate_path = f'certificates/{email}_{skill.replace(" ", "_")}.pdf'
        os.makedirs('certificates', exist_ok=True)
        self.pdf.output(certificate_path)
        
        return certificate_path 