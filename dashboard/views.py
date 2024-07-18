from datetime import date

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from appointment.models import Appointment
from .serializers import AppointmentListSerializer, AppointmentDetailsSerializer


class AppointmentListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentListSerializer

    @extend_schema(
        description="Retrieve list of appointments for today or a specific stylist.",
        parameters=[
            OpenApiParameter("stylist", type=str, location=OpenApiParameter.QUERY,
                             description="Filter appointments by stylist name."),
        ],
        responses={
            200: OpenApiResponse(description=AppointmentListSerializer(many=True)),
            400: OpenApiResponse(description="Bad Request"),
            500: OpenApiResponse(description="Internal Server Error")
        }
    )
    def get(self, request, format=None):
        stylist = request.query_params.get('stylist', None)
        today = date.today()

        try:
            if stylist:
                appointments = Appointment.objects.filter(stylist=stylist, date=today).order_by('time')
            else:
                appointments = Appointment.objects.filter(date=today).order_by('time')
            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentDetailsSerializer

    @extend_schema(
        description="Retrieve details of a specific appointment by ticket number.",
        parameters=[
            OpenApiParameter("ticket_number", type=str, location=OpenApiParameter.PATH,
                             description="Ticket number of the appointment."),
        ],
        responses={
            200: OpenApiResponse(description=AppointmentDetailsSerializer),
            404: OpenApiResponse(description="Appointment not found"),
            500: OpenApiResponse(description="Internal Server Error")
        }
    )
    def get(self, request, ticket_number, format=None):
        try:
            appointment = get_object_or_404(Appointment, ticket_number=ticket_number)
            serializer = self.serializer_class(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        logout(request)
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)