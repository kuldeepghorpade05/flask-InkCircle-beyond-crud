import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery

# Initialize Celery
celery = Celery('celery_tasks')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'

# HARDCODE YOUR EMAIL CONFIG - TEMPORARY FIX
EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'kuldeepghorpade1010@gmail.com',  # Your email
    'MAIL_PASSWORD': 'hfovprccmehlojsh',  # Your app password
    'MAIL_DEFAULT_SENDER': 'kuldeep Ghorpade <kuldeepghorpade1010@gmail.com>'
}

@celery.task(name='celery_tasks.send_email')
def send_email(recipients, subject, html_body, text_body=None):
    """Celery task to send email in background"""
    try:
        print(f"📧 [CELERY] Starting email send to {recipients}")
        print(f"📧 [CELERY] Username: {EMAIL_CONFIG['MAIL_USERNAME']}")
        print(f"📧 [CELERY] Password: {'*' * len(EMAIL_CONFIG['MAIL_PASSWORD'])}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['MAIL_DEFAULT_SENDER']
        msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients

        # Create HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send email
        print(f"📧 [CELERY] Connecting to {EMAIL_CONFIG['MAIL_SERVER']}:{EMAIL_CONFIG['MAIL_PORT']}")
        
        with smtplib.SMTP(EMAIL_CONFIG['MAIL_SERVER'], EMAIL_CONFIG['MAIL_PORT']) as server:
            server.starttls()
            print("✅ [CELERY] TLS started")
            
            print(f"📧 [CELERY] Logging in...")
            server.login(EMAIL_CONFIG['MAIL_USERNAME'], EMAIL_CONFIG['MAIL_PASSWORD'])
            print("✅ [CELERY] SMTP login successful")
            
            server.send_message(msg)
            print(f"✅ [CELERY] Email sent successfully to {recipients}")
        
        return {"status": "success", "message": "Email sent!"}
        
    except Exception as e:
        print(f"❌ [CELERY] Failed to send email: {str(e)}")
        return {"status": "failed", "error": str(e)}