from rest_framework import serializers
from appointment.models import Appointment
from .models import User


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
            'style_sample'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=120)
    password = serializers.CharField(max_length=150, min_length=6, write_only=True)

