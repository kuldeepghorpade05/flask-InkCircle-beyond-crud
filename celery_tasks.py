import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Celery
celery = Celery('celery_tasks') 
celery.conf.broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0') # redis as broker
celery.conf.result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0') # backend storing results - using redis here

@celery.task(name='celery_tasks.send_email')
def send_email(recipients, subject, html_body, text_body=None):
    """Celery task to send email in background"""
    try:
        print(f"📧 [CELERY] Starting email send to {recipients}")
        
        # Get config from environment
        mail_config = {
            'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
            'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
            'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER')
        }
        
        # Validate required config
        if not mail_config['MAIL_USERNAME'] or not mail_config['MAIL_PASSWORD']:
            return {"status": "failed", "error": "Email configuration missing"}
        
        # message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_config['MAIL_DEFAULT_SENDER']
        msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients

        # HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send email
        print(f"📧 [CELERY] Connecting to {mail_config['MAIL_SERVER']}:{mail_config['MAIL_PORT']}")
        
        with smtplib.SMTP(mail_config['MAIL_SERVER'], mail_config['MAIL_PORT']) as server:
            if mail_config['MAIL_USE_TLS']:
                server.starttls()
                print("✅ [CELERY] TLS started")
            
            print(f"📧 [CELERY] Logging in...")
            server.login(mail_config['MAIL_USERNAME'], mail_config['MAIL_PASSWORD'])
            print("✅ [CELERY] SMTP login successful")
            
            server.send_message(msg)
            print(f"✅ [CELERY] Email sent successfully to {recipients}")
        
        return {"status": "success", "message": "Email sent!"}
        
    except Exception as e:
        print(f"❌ [CELERY] Failed to send email: {str(e)}")
        return {"status": "failed", "error": str(e)}