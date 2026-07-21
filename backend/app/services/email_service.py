import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from datetime import datetime
from app.config import EMAIL, EMAIL_PASSWORD

logger = logging.getLogger(__name__)

def send_welcome_email(full_name: str, email: str, role_name: str, store_name: str, store_id: str):
    if not EMAIL or not EMAIL_PASSWORD:
        logger.error("Email credentials not configured. Skipping welcome email.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = "Restaurant Dashboard Login Notification"

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        body = f"""Hello {full_name},

You have successfully logged into the Restaurant Dashboard.

Login Details

Full Name:
{full_name}

Email:
{email}

Role:
{role_name}

Store:
{store_name}

Store ID:
{store_id}

Login Time:
{current_time}

Thank you.

Restaurant Dashboard Team
"""
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")

def send_account_creation_email(
    full_name: str, 
    email: str, 
    role: str, 
    region: str, 
    district: str, 
    store_name: str, 
    store_id: str, 
    emp_id: str,
    temp_password: str = None
):
    if not EMAIL or not EMAIL_PASSWORD:
        logger.error("Email credentials not configured. Skipping account creation email.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = "Welcome to Restaurant Operations Management System"

        body = f"""Hello {full_name},

Your account has been created successfully.

Employee ID:
{emp_id}

Role:
{role}

Assigned Region:
{region}

Assigned District:
{district}

Assigned Store:
{store_name}

Login Email:
{email}

"""
        if temp_password:
            body += f"""Temporary Password:
{temp_password}

"""

        body += """Login URL:
http://localhost:3000/login

For security reasons, you must change your password immediately after your first login.

Regards,
Restaurant Operations Team
"""

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Failed to send account creation email to {email}: {e}")
