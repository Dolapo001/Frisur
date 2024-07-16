from django.db import models, IntegrityError
import uuid
import base64
import random

STYLIST_CHOICES = (
    ('pastor', 'Pastor'),
    ('orebiyi', 'Orebiyi'),
    ('femi', 'Femi'),
    ('random', 'Random')
)

SERVICE_TYPE_CHOICES = (
    ('trimming', 'Trimming'),
    ('haircut', 'Haircut'),
    ('shaving', 'Shaving'),
)

STATUS_CHOICES = (
    ('scheduled', 'Scheduled'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled')
)


class Appointment(models.Model):
    ticket_number = models.CharField(max_length=12, unique=True, primary_key=True, editable=False)
    date = models.DateField()
    time = models.TimeField()
    stylist = models.CharField(max_length=20, choices=STYLIST_CHOICES)
    service = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('date', 'time', 'stylist')

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            hex_string = uuid.uuid4().hex
            bytes_data = bytes.fromhex(hex_string)
            data = base64.urlsafe_b64encode(bytes_data).decode('ascii')[:12]
            self.ticket_number = data.replace("-", "")

        if self.stylist == 'random':
            stylists = [choice[0] for choice in STYLIST_CHOICES if choice[0] != 'random']
            self.stylist = random.choice(stylists) if stylists else None

        if Appointment.objects.filter(date=self.date, time=self.time, stylist=self.stylist).exists():
            raise IntegrityError(
                f"An appointment with {self.stylist} for {self.date} at {self.time} has already been scheduled."
            )

        super().save(*args, **kwargs)
