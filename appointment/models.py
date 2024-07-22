from django.db import models, IntegrityError
from datetime import datetime, timedelta
import random
from django.utils import timezone


STYLIST_CHOICES = (
    ('Pastor', 'Pastor'),
    ('Orebiyi', 'Orebiyi'),
    ('Femi', 'Femi'),
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
    ticket_number = models.CharField(max_length=4, unique=True, primary_key=True, editable=False)
    date = models.DateField()
    time = models.TimeField()
    stylist = models.CharField(max_length=20, choices=STYLIST_CHOICES)
    service = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    customer_firstname = models.CharField(max_length=200)
    customer_lastname = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(null=True, blank=True)
    special_request = models.TextField(null=True, blank=True)
    end_time = models.TimeField(null=True)
    datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('date', 'time', 'stylist')

    @property
    def customer_name(self):
        if self.customer_lastname:
            return f"{self.customer_firstname} {self.customer_lastname}"
        else:
            return self.customer_firstname

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
            numbers = ''.join(random.choices('0123456789', k=2))
            self.ticket_number = f"{letters}{numbers}"

        if self.stylist == 'random':
            stylists = [choice[0] for choice in STYLIST_CHOICES if choice[0] != 'random']
            self.stylist = random.choice(stylists) if stylists else None

        # Fixed duration of 30 minutes
        duration = 30
        start_time = self.time
        appointment_start_time = datetime.combine(self.date, start_time)
        appointment_end_time = appointment_start_time + timedelta(minutes=duration)
        self.end_time = appointment_end_time.time()

        self.datetime = timezone.make_aware(datetime.combine(self.date, self.time))

        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            date=self.date,
            stylist=self.stylist,
            time__lt=self.end_time,
            time__gte=self.time
        ).exclude(pk=self.pk)  # Exclude current instance if updating

        if overlapping_appointments.exists():
            raise IntegrityError(
                f"An appointment with {self.stylist} between {self.time} and {self.end_time} on {self.date} "
                f"has already been scheduled."
            )

        super().save(*args, **kwargs)
