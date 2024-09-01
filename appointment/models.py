from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from cloudinary.models import CloudinaryField
import os
import random
from datetime import datetime, timedelta


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
    end_time = models.TimeField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    style_sample = models.ImageField(upload_to='images/', blank=True, null=True)

    class Meta:
        db_table = 'appointment_appointment'

    @property
    def customer_name(self):
        return f"{self.customer_firstname} {self.customer_lastname}" if self.customer_lastname else self.customer_firstname

    def generate_ticket_number(self):
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        numbers = ''.join(random.choices('0123456789', k=2))
        return f"{letters}{numbers}"

    def determine_stylist(self):
        if self.stylist == 'Any':
            stylists = [choice[0] for choice in STYLIST_CHOICES if choice[0] != 'Any']
            self.stylist = random.choice(stylists) if stylists else None

    def set_end_time(self, duration=30):
        if not self.time:
            raise ValueError("Start time must be set before determining end time.")
        appointment_start_time = datetime.combine(self.date, self.time)
        appointment_end_time = appointment_start_time + timedelta(minutes=duration)
        self.end_time = appointment_end_time.time()

    def check_overlapping_appointments(self):
        if not self.end_time:
            self.set_end_time()

        appointment_end_time = datetime.combine(self.date, self.end_time)

        if not self.pk:
            overlapping_appointments = Appointment.objects.filter(
                date=self.date,
                stylist=self.stylist,
                end_time__gt=self.time,
                time__lt=self.end_time
            )
        else:
            overlapping_appointments = Appointment.objects.filter(
                date=self.date,
                stylist=self.stylist,
                end_time__gt=self.time,
                time__lt=self.end_time
            ).exclude(pk=self.pk)

        if overlapping_appointments.exists():
            raise IntegrityError(
                f"An appointment with the stylist {self.stylist} at {self.time} on {self.date} already exists."
            )

    def block_stylist_availability_for_home_service(self):
        if self.service == 'home_service':
            home_service_duration = timedelta(hours=3)
            appointment_start_time = datetime.combine(self.date, self.time)
            appointment_end_time = appointment_start_time + home_service_duration

            overlapping_appointments = Appointment.objects.filter(
                stylist=self.stylist,
                date=self.date,
                time__lt=appointment_end_time,
                end_time__gt=self.time
            ).exclude(pk=self.pk)

            if overlapping_appointments.exists():
                raise IntegrityError(
                    f"The stylist {self.stylist} is not available for the selected time and service."
                )

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()

        self.determine_stylist()
        self.set_end_time()
        self.datetime = timezone.make_aware(datetime.combine(self.date, self.time), timezone.get_current_timezone())
        self.check_overlapping_appointments()
        self.block_stylist_availability_for_home_service()
        super().save(*args, **kwargs)
