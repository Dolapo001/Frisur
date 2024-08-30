import os.path
import uuid
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from datetime import datetime, timedelta
import random
from django.utils import timezone
#from cloudinary.models import CloudinaryField



STYLIST_CHOICES = (
    ('Pastor', 'Pastor'),
    ('Orebiyi', 'Orebiyi'),
    ('Femi', 'Femi'),
    ('Any', 'Any')
)

SERVICE_TYPE_CHOICES = (
    ('trimming', 'Trimming'),
    ('haircut', 'Haircut'),
    ('shaving', 'Shaving'),
    ('home_service', 'Home Service')
)

STATUS_CHOICES = (
    ('scheduled', 'Scheduled'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled')
)


class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    ticket_number = models.CharField(max_length=4, unique=True, editable=False)
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
    #style_sample = CloudinaryField('image', null=True, blank=True)

    class Meta:
        unique_together = ('date', 'time', 'stylist')
        db_table = 'appointment_appointment'

    @property
    def customer_name(self):
        if self.customer_lastname:
            return f"{self.customer_firstname} {self.customer_lastname}"
        else:
            return self.customer_firstname

    def generate_ticket_number(self):
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        numbers = ''.join(random.choices('0123456789', k=2))
        return f"{letters}{numbers}"

    def determine_stylist(self):
        if self.stylist == 'random':
            stylists = [choice[0] for choice in STYLIST_CHOICES if choice[0] != 'random']
            self.stylist = random.choice(stylists) if stylists else None

    def set_end_time(self):
        duration = 30
        start_time = self.time
        appointment_start_time = datetime.combine(self.date, start_time)
        appointment_end_time = appointment_start_time + timedelta(minutes=duration)
        self.end_time = appointment_end_time.time()

    def check_overlapping_appointments(self):
        if not self.pk:
            overlapping_appointments = Appointment.objects.filter(
                date=self.date,
                time=self.time,
                stylist=self.stylist
            )
            if overlapping_appointments.exists():
                raise IntegrityError(
                    f"An appointment with {self.stylist} at {self.time} on {self.date} already exists."
                )

    def block_stylist_availability_for_home_service(self):
        if self.service == 'home_service':
            home_service_duration = timedelta(hours=3)
            start_time = datetime.combine(self.date, self.time) - timedelta(hours=1)
            end_time = start_time + home_service_duration

            overlapping_appointments = Appointment.objects.filter(
                stylist=self.stylist,
                date=self.date,
                time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping_appointments.exists():
                raise IntegrityError(
                    f"The stylist {self.stylist} is not available for the selected time and service."
                )

    def clean(self):
        if self.style_sample:
            allowed_extensions = ['.jpg', '.jpeg', '.png']
            extension = os.path.splitext(self.style_sample.name)[1].lower()
            if extension not in allowed_extensions:
                raise ValidationError(f"Unsupported file extension. Allowed extensions are: {", ".join(allowed_extensions)}")

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()

        self.determine_stylist()
        self.set_end_time()
        self.datetime = timezone.make_aware(datetime.combine(self.date, self.time), timezone.get_current_timezone())
        self.check_overlapping_appointments()
        self.block_stylist_availability_for_home_service()
        self.clean()
        super().save(*args, **kwargs)
