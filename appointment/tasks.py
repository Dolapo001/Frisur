from celery import shared_task
from .models import Appointment
from .email_utils import send_reminder_email
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_reminder_email_task(ticket_number):
    logger.info(f"Received task for ticket number: {ticket_number}")
    try:
        appointment = Appointment.objects.get(ticket_number=ticket_number)
        send_reminder_email(None, appointment)
        logger.info(f"Reminder email sent for ticket number: {ticket_number}")
    except Appointment.DoesNotExist:
        logger.error(f"Appointment with ticket number {ticket_number} does not exist.")
    except Exception as e:
        logger.error(f"Error in send_reminder_email_task: {str(e)}")
