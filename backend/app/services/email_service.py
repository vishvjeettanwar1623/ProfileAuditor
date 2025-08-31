import os
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import SendGrid (if available)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Get email configuration from environment variables
EMAIL_FROM = os.getenv("EMAIL_FROM", "recruiter@profileauditor.ai")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_interview_invitation(
    email: str,
    name: str,
    score: float,
    message: Optional[str] = None,
    interview_date: Optional[str] = None,
    interview_location: Optional[str] = None
) -> bool:
    """Send interview invitation email to candidate"""
    # Create email subject
    subject = f"Interview Invitation - ProfileAuditor"
    
    # Create email body
    body = create_email_body(
        name=name,
        score=score,
        message=message,
        interview_date=interview_date,
        interview_location=interview_location
    )
    
    # Send email using SMTP (SendGrid disabled)
    return send_with_smtp(email, subject, body)

def create_email_body(
    name: str,
    score: float,
    message: Optional[str] = None,
    interview_date: Optional[str] = None,
    interview_location: Optional[str] = None
) -> str:
    """Create email body for interview invitation"""
    # Default message if not provided
    if not message:
        message = "We were impressed with your qualifications and would like to invite you for an interview."
    
    # Create email body
    body = f"""
    <html>
    <body>
        <h2>Interview Invitation</h2>
        <p>Dear {name},</p>
        <p>{message}</p>
        <p>Your Reality Score: <strong>{score:.1f}/100</strong></p>
    """
    
    # Add interview details if provided
    if interview_date:
        body += f"<p><strong>Interview Date:</strong> {interview_date}</p>"
    if interview_location:
        body += f"<p><strong>Interview Location:</strong> {interview_location}</p>"
    
    # Add closing
    body += f"""
        <p>Please confirm your availability by replying to this email.</p>
        <p>Best regards,<br>Recruitment Team<br>ProfileAuditor</p>
    </body>
    </html>
    """
    
    return body

def send_with_sendgrid(to_email: str, subject: str, body: str) -> bool:
    """Send email using SendGrid"""
    try:
        # Create SendGrid message
        message = Mail(
            from_email=EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Check if email was sent successfully
        return response.status_code in [200, 201, 202]
    
    except Exception as e:
        print(f"Error sending email with SendGrid: {str(e)}")
        return False

def send_with_smtp(to_email: str, subject: str, body: str) -> bool:
    """Send email using SMTP"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        # Attach body
        message.attach(MIMEText(body, "html"))
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            
            # Login with credentials
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                
                # Send email
                server.send_message(message)
                
                # Log success
                print(f"✅ Email sent successfully to: {to_email}")
                print(f"📧 Subject: {subject}")
                return True
            else:
                print("❌ SMTP credentials not configured")
                return False
    
    except Exception as e:
        print(f"❌ Error sending email with SMTP: {str(e)}")
        return False