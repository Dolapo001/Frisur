from rest_framework import serializers
from .models import Appointment


class ScheduleAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'stylist', 'service', 'customer_firstname', 'customer_lastname', 'customer_email',
                  'customer_phone']

    def create(self, validated_data):
        appointment = Appointment.objects.create(**validated_data)
        return appointment


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
        fields = ['ticket_number', 'date', 'time', 'stylist', 'service', 'customer_name', 'customer_email',
                  'customer_phone', 'status']


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['ticket_number']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['feedback']
