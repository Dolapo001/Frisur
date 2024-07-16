import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_confirmation_email(appointment):
    subject = 'Appointment Confirmation'
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = [appointment.customer_email]

    context = {
        'customer_firstname': appointment.customer_firstname,
        'stylist': appointment.stylist,
        'date': appointment.date,
        'time': appointment.time,
        'service': appointment.service,
        'ticket_number': appointment.ticket_number,
        'email_sender_name': settings.EMAIL_SENDER_NAME,
    }

    email_html_message = render_to_string('appointment_confirmation_email.html', context)
    email_plain_message = render_to_string('confirmation_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, email_plain_message, sender, recipient)
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
        logger.info(f"Email sent successfully to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")

