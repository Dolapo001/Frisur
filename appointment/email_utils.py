import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import os
import time

# Environment variables
GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
EMAIL_SENDER_NAME = os.getenv('EMAIL_SENDER_NAME')
EMAIL_SENDER_ADDRESS = os.getenv('EMAIL_SENDER_ADDRESS')

# Email authentication configuration
auth = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'use_tls': True,
    'username': GMAIL_USERNAME,
    'password': GMAIL_PASSWORD
}

# Function to render email template
def render_email_template(template_path, context):
    with open(template_path, 'r') as file:
        template = Template(file.read())
    return template.render(context)

# Function to send appointment confirmation email
def send_appointment_confirmation(to, appointment_details, max_retries=3):
    confirmation_template_path = os.path.join(
        os.path.dirname(__file__),
        "templates/appointment_confirmation_email.html"
    )
    email_html = render_email_template(confirmation_template_path, appointment_details)
    msg = MIMEMultipart()
    msg['From'] = f"{EMAIL_SENDER_NAME} <{EMAIL_SENDER_ADDRESS}>"
    msg['To'] = to
    msg['Subject'] = "Appointment Confirmation"
    msg.attach(MIMEText(email_html, 'html'))

    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(auth['host'], auth['port']) as server:
                if auth['use_tls']:
                    server.starttls()
                server.login(auth['username'], auth['password'])
                server.send_message(msg)
                print("Email sent successfully!")
                return
        except Exception as e:
            print(f"Attempt {attempt + 1} - Error: {e}")
            if attempt + 1 < max_retries:
                print("Retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                print("Failed to send email after several attempts.")
