from datetime import timedelta
from django.utils import timezone
from .tasks import send_reminder_email_task
import logging

logger = logging.getLogger(__name__)


def schedule_reminder_email(appointment):
    reminder_time = appointment.datetime - timedelta(hours=1)
    now = timezone.now()
    delay = reminder_time - now

    if delay.total_seconds() > 0:
        send_reminder_email_task.apply_async(
            args=[appointment.ticket_number],
            eta=reminder_time
        )
    else:
        logger.info(f"Appointment {appointment.ticket_number} is already past the reminder time.")