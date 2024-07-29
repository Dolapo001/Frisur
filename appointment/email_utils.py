import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def get_absolute_url(view_name, *args):
    base_url = settings.SITE_DOMAIN
    relative_url = reverse(view_name, args=args)
    return base_url.rstrip('/') + '/' + relative_url.lstrip('/')


def send_confirmation_email(appointment):
    subject = 'Appointment Confirmation'
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = [appointment.customer_email]

    reschedule_url = get_absolute_url('reschedule-appointment', appointment.ticket_number)
    cancel_url = get_absolute_url('cancel-appointment', appointment.ticket_number)

    context = {
        'customer_firstname': appointment.customer_firstname,
        'stylist': appointment.stylist,
        'date': appointment.date,
        'time': appointment.time,
        'end_time': appointment.end_time,
        'service': appointment.service,
        'ticket_number': appointment.ticket_number,
        'email_sender_name': settings.EMAIL_SENDER_NAME,
        'reschedule_url': reschedule_url,
        'cancel_url': cancel_url,
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


def send_status_update_email(request, appointment, status, new_date=None, new_time=None, new_stylist=None,
                             new_end_time=None):
    subject = f'Appointment {status.capitalize()}'
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = [appointment.customer_email]

    context = {
        'customer_firstname': appointment.customer_firstname,
        'status': status,
        'stylist': new_stylist if new_stylist != 'random' else appointment.stylist,
        'service': appointment.service,
        'ticket_number': appointment.ticket_number,
        'email_sender_name': settings.EMAIL_SENDER_NAME,
        'new_date': new_date,
        'new_time': new_time,
        'new_end_time': new_end_time
    }
    email_html_message = render_to_string('appointment_status_update_email.html', context)
    email_plain_message = render_to_string('status_update_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, email_plain_message, sender, recipient)
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
        logger.info(f"Status update email sent successfully to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send status update email to {recipient}: {str(e)}")


def send_reminder_email(appointment):
    subject = 'Appointment Reminder'
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = [appointment.customer_email]

    # Determine URL
    reschedule_url = get_absolute_url('reschedule-appointment', appointment.ticket_number)
    cancel_url = get_absolute_url('cancel-appointment', appointment.ticket_number)

    context = {
        'customer_firstname': appointment.customer_firstname,
        'stylist': appointment.stylist,
        'date': appointment.date,
        'time': appointment.time,
        'end_time': appointment.end_time,
        'service': appointment.service,
        'ticket_number': appointment.ticket_number,
        'email_sender_name': settings.EMAIL_SENDER_NAME,
        'reschedule_url': reschedule_url,
        'cancel_url': cancel_url,
    }
    email_html_message = render_to_string('appointment_reminder_email.html', context)
    email_plain_message = render_to_string('reminder_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, email_plain_message, sender, recipient)
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
        logger.info(f"Email sent successfully to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")

