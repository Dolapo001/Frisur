from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, STYLIST_CHOICES
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist


class ScheduleAppointmentView(APIView):
    serializer_class = ScheduleAppointmentSerializer

    @transaction.atomic
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                try:
                    appointment = serializer.save()
                    confirm_serializer = ConfirmAppointmentSerializer(appointment)
                    # confirmation message logic here
                    return Response(confirm_serializer.data, status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response({
                        "error_message": "An appointment with the specified date, time, and stylist already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while scheduling appointment: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RescheduleAppointmentView(APIView):
    serializer_class = RescheduleAppointmentSerializer

    @transaction.atomic
    def put(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(appointment, data=request.data)
        if serializer.is_valid():
            new_date = serializer.validated_data.get('date')
            new_time = serializer.validated_data.get('time')
            new_stylist = serializer.validated_data.get('stylist')

            if new_date:
                appointment.date = new_date
            if new_time:
                appointment.time = new_time
            if new_stylist:
                if new_stylist not in dict(STYLIST_CHOICES).keys():
                    return Response({"error": "Invalid stylist"}, status=status.HTTP_400_BAD_REQUEST)
                appointment.stylist = new_stylist

                # Check for double-booking
            if Appointment.objects.filter(date=appointment.date, time=appointment.time,
                                          stylist=appointment.stylist).exclude(ticket_number=ticket_number).exists():
                return Response({"error": "This time slot is already booked for the selected stylist."},
                                status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'rescheduled'
            appointment.save()

            # Confirmation message logic can be added here if needed

            return Response(ConfirmAppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentView(APIView):
    @transaction.atomic
    def delete(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except ObjectDoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        # Directly update the status to 'cancelled' without calling save()
        Appointment.objects.filter(ticket_number=ticket_number).update(status='cancelled')

        # cancellation confirmation message logic
        return Response({"message": "Appointment cancelled"}, status=status.HTTP_200_OK)


class ConfirmAppointmentView(APIView):
    serializer_class = ConfirmAppointmentSerializer

    @transaction.atomic
    def get(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except ObjectDoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        if appointment.status == 'cancelled':
            return Response({"error": "Cannot confirm a cancelled appointment"}, status=status.HTTP_400_BAD_REQUEST)

        # confirmation message
        serializer = self.serializer_class(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)



