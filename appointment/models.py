from django.db import models, IntegrityError
import uuid
import base64
import random

stylist_choices = (
    ('pastor', 'Pastor'),
    ('orebiyi', 'Orebiyi'),
    ('femi', 'Femi'),
    ('random', 'Random')
)

service_type = (
    ('trimming', 'Trimming'),
    ('haircut', 'Haircut'),
    ('shaving', 'Shaving'),
)

status_choices = (
    ('scheduled', 'Scheduled'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled')
)


class Stylist(models.Model):
    stylist = models.CharField(max_length=20, choices=stylist_choices)
    id = models.CharField(max_length=12, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.stylist

    def save(self, *args, **kwargs):
        if not self.id:
            hex_string = uuid.uuid4().hex
            bytes_data = bytes.fromhex(hex_string)
            data = base64.urlsafe_b64encode(bytes_data).decode('ascii')[:12]
            self.id = data.replace("-", "")

        super().save(*args, **kwargs)


class Service(models.Model):
    service = models.CharField(max_length=20, choices=service_type)
    id = models.CharField(max_length=12, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.service

    def save(self, *args, **kwargs):
        if not self.id:
            hex_string = uuid.uuid4().hex
            bytes_data = bytes.fromhex(hex_string)
            data = base64.urlsafe_b64encode(bytes_data).decode('ascii')[:12]
            self.id = data.replace("-", "")

        super().save(*args, **kwargs)


class Appointment(models.Model):
    ticket_number = models.CharField(max_length=12, unique=True, primary_key=True, editable=False)
    date = models.DateField()
    time = models.TimeField()
    stylist = models.ForeignKey(Stylist, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=status_choices)
    feedback = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('date', 'time', 'stylist')

    def __str__(self):
        return self.ticket_number

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            hex_string = uuid.uuid4().hex
            bytes_data = bytes.fromhex(hex_string)
            data = base64.urlsafe_b64encode(bytes_data).decode('ascii')[:12]
            self.ticket_number = data.replace("-", "")

        if self.stylist and self.stylist.stylist == 'random':
            stylists = Stylist.objects.exclude(stylist='random')
            self.stylist = random.choice(stylists) if stylists else None

        if Appointment.objects.filter(date=self.date, time=self.time, stylist=self.stylist).exists():
            raise IntegrityError(
                f"An appointment with {self.stylist} for {self.date} at {self.time} has already been scheduled.")

        super().save(*args, **kwargs)
