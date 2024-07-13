from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, Stylist
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist


class ScheduleAppointmentView(APIView):
    serializer_class = ScheduleAppointmentSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                appointment = serializer.save()
                # confirmation message logic here
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while scheduling appointment: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RescheduleAppointmentView(APIView):
    serializer_class = RescheduleAppointmentSerializer

    def put(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(appointment, data=request.data)
        if serializer.is_valid():
            new_date = serializer.validated_data.get('date')
            new_time = serializer.validated_data.get('time')
            new_stylist_id = serializer.validated_data.get('stylist')

            if new_date:
                appointment.date = new_date
            if new_time:
                appointment.time = new_time
            if new_stylist_id:
                try:
                    new_stylist = Stylist.objects.get(id=new_stylist_id)
                    appointment.stylist = new_stylist
                except Stylist.DoesNotExist:
                    return Response({"error": "Stylist not found"}, status=status.HTTP_404_NOT_FOUND)

            appointment.status = 'rescheduled'
            appointment.save()

            # Confirmation message logic can be added here if needed

            return Response(ConfirmAppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentView(APIView):
    def delete(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except ObjectDoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        appointment.status = 'cancelled'
        appointment.save()

        # cancellation confirmation message
        return Response({"message": "Appointment cancelled"}, status=status.HTTP_200_OK)
