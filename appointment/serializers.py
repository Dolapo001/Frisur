from rest_framework import serializers
from .models import Appointment
from .email_utils import send_appointment_confirmation



class ScheduleAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'stylist', 'service', 'customer_name', 'customer_email', 'customer_phone']

    def create(self, validated_data):
        appointment = Appointment.objects.create(**validated_data)
        self.send_confirmation_email(appointment)
        return appointment

    def send_confirmation_email(self, appointment):
        stylist_name = dict(Appointment._meta.get_field('stylist').choices).get(appointment.stylist, 'Unknown')
        service_type_name = dict(Appointment._meta.get_field('service').choices).get(appointment.service, 'Unknown')
        appointment_details = {
            'stylist': stylist_name,
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M'),
            'service_type': service_type_name,
            'ticket_number': appointment.ticket_number,
            'customer_name': appointment.customer_name,
            'customer_email': appointment.customer_email
        }
        send_appointment_confirmation(appointment.customer_email, appointment_details)


class RescheduleAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'stylist', 'service']


class CancelAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['ticket_number']


class ConfirmAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['ticket_number', 'date', 'time', 'stylist', 'service', 'customer_name', 'customer_email', 'customer_phone', 'status']


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['ticket_number']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['feedback']
