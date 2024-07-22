from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from appointment.models import Appointment
from appointment.utils import schedule_reminder_email


class Command(BaseCommand):
    help = 'Schedule reminder emails for upcoming appointments'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Filter for appointments within the next 1 hour
        future_threshold = now + timedelta(hours=1)
        appointments = Appointment.objects.filter(datetime__range=(now, future_threshold))

        for appointment in appointments:
            schedule_reminder_email(appointment)