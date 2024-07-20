from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, STYLIST_CHOICES
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
from .email_utils import send_confirmation_email, send_status_update_email
from .tasks import send_reminder_email_task


class ScheduleAppointmentView(APIView):
    serializer_class = ScheduleAppointmentSerializer

    @extend_schema(
        request=ScheduleAppointmentSerializer,
        responses={
            201: OpenApiResponse(response=ConfirmAppointmentSerializer),
            500: OpenApiResponse(description="Internal Server Error"),
            400: OpenApiResponse(description="An appointment with the specified date, time, and stylist already exists.")
        },
        description="Endpoint to schedule a new appointment."
    )
    @transaction.atomic
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                try:
                    appointment = serializer.save()
                    send_confirmation_email(request, appointment)
                    reminder_time = appointment.datetime - timedelta(hours=1)
                    send_reminder_email_task.apply_async((appointment.ticket_number,), eta=reminder_time)
                    confirm_serializer = ConfirmAppointmentSerializer(appointment)
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

    @extend_schema(
        request=RescheduleAppointmentSerializer,
        parameters=[
            OpenApiParameter("ticket_number", type=str, location=OpenApiParameter.PATH,
                             description="Ticket number of the appointment to reschedule")
        ],
        responses={
            201: OpenApiResponse(response=ConfirmAppointmentSerializer),
            400: OpenApiResponse(description="This time slot is already booked for the selected stylist."),
            404: OpenApiResponse(description="Appointment not found."),
            500: OpenApiResponse(description="Internal Server Error.")
        },
        description="Endpoint to reschedule an existing appointment."
    )
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
            new_end_time = serializer.validated_data.get('end_time')
            new_stylist = serializer.validated_data.get('stylist')

            if new_date:
                appointment.date = new_date
            if new_time:
                appointment.time = new_time
            if new_end_time:
                appointment.end_time = new_end_time
            if new_stylist:
                if new_stylist not in dict(STYLIST_CHOICES).keys():
                    return Response({"error": "Invalid stylist"}, status=status.HTTP_400_BAD_REQUEST)
                appointment.stylist = new_stylist

            if Appointment.objects.filter(date=appointment.date, time=appointment.time,
                                          stylist=appointment.stylist).exclude(ticket_number=ticket_number).exists():
                return Response({"error": "This time slot is already booked for the selected stylist."},
                                status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'rescheduled'
            appointment.save()

            send_status_update_email(request, appointment, 'rescheduled', new_date, new_time, new_end_time, new_stylist)
            reminder_time = appointment.datetime - timedelta(hours=1)
            send_reminder_email_task.apply_async((appointment.ticket_number,), eta=reminder_time)

            return Response(ConfirmAppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentView(APIView):
    @extend_schema(
        request=RescheduleAppointmentSerializer,
        parameters=[
            OpenApiParameter("ticket_number", type=str, location=OpenApiParameter.PATH,
                             description="Ticket number of the appointment to cancel")
        ],
        responses={
            201: OpenApiResponse(response="Cancelled."),
            404: OpenApiResponse(description="Appointment not found."),
            500: OpenApiResponse(description="Internal Server Error.")
        },
        description="Endpoint to cancel an existing appointment."
    )
    @transaction.atomic
    def delete(self, request, ticket_number):
        try:
            appointment = Appointment.objects.get(ticket_number=ticket_number)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        Appointment.objects.filter(ticket_number=ticket_number).update(status='cancelled')

        send_status_update_email(request, appointment, status='cancelled')

        return Response({"message": "Appointment cancelled"}, status=status.HTTP_200_OK)


class ConfirmAppointmentView(APIView):
    serializer_class = ConfirmAppointmentSerializer

    @extend_schema(
        request=RescheduleAppointmentSerializer,
        parameters=[
            OpenApiParameter("ticket_number", type=str, location=OpenApiParameter.PATH,
                             description="Ticket number of the appointment for confirmation")
        ],
        responses={
            200: OpenApiResponse(response="OK."),
            400: OpenApiResponse(response="Cannot get details of a cancelled appointment."),
            404: OpenApiResponse(description="Appointment not found."),
            500: OpenApiResponse(description="Internal Server Error.")
        },
        description="Endpoint to get details of an existing appointment."
    )
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
