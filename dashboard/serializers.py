from rest_framework import serializers
from appointment.models import Appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField()

    class Meta:
        model = Appointment
        fields = [
            'customer_name',
            'ticket_number',
            'stylist',
            'date',
            'time',
            'end_time',
            'special_request'
        ]


class AppointmentDetailsSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField()

    class Meta:
        model = Appointment
        fields = [
            'ticket_number',
            'date',
            'time',
            'end_time',
            'customer_name',
            'customer_email',
            'customer_phone',
            'service',
            'special_request',
        ]
