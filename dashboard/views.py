from datetime import date, datetime
from django.contrib.auth import authenticate, login, logout
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from appointment.models import Appointment
from .serializers import AppointmentListSerializer, AppointmentDetailsSerializer, UserSerializer, LoginSerializer


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
            200: OpenApiResponse(
                description="List of appointments",
                response=AppointmentListSerializer(many=True)
            ),
            400: OpenApiResponse(description="Bad Request"),
            500: OpenApiResponse(description="Internal Server Error")
        }
    )
    def get(self, request, format=None):
        stylist = request.query_params.get('stylist', None)
        today = date.today()

        try:
            if stylist:
                appointments = Appointment.objects.filter(
                    stylist=stylist,
                    date=today,
                    status__in=['scheduled', 'rescheduled']  # Exclude cancelled appointments
                ).order_by('time')
            else:
                appointments = Appointment.objects.filter(
                    date=today,
                    status__in=['scheduled', 'rescheduled']  # Exclude cancelled appointments
                ).order_by('time')

            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.
                            HTTP_500_INTERNAL_SERVER_ERROR)


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
            200: OpenApiResponse(
                description="Appointment details",
                response=AppointmentDetailsSerializer
            ),
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
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.
                            HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        description="Log in a user with username and password.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Login successful",
                #response=UserSerializer
            ),
            401: OpenApiResponse(description="Invalid credentials")
        }
    )
    def post(self, request, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username = validated_data["username"]
        password = validated_data["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            tokens = {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
            return Response(
                data={
                    "username": user.username,
                    "tokens": tokens
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data['access']
        return Response({
            "message": "Refreshed successfully",
            "token": access_token,
            "status": "success"
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Log out the currently authenticated user.",
        responses={
            200: OpenApiResponse(description="Logout successful"),
            401: OpenApiResponse(description="Unauthorized - user not logged in")
        }
    )
    def post(self, request, format=None):
        logout(request)
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)


class StylistAppointmentListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentListSerializer

    def get(self, request, *args, **kwargs):
        stylist = request.query_params.get('stylist', None)
        if stylist:
            appointments = Appointment.objects.filter(stylist=stylist)
        else:
            appointments = Appointment.objects.all()

        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentListByDayView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentListSerializer

    @extend_schema(
        description="Retrieve list of appointments for a specific day.",
        parameters=[
            OpenApiParameter("date", type=str, location=OpenApiParameter.QUERY,
                             description="Filter appointments by date (YYYY-MM-DD)."),
            OpenApiParameter("stylist", type=str, location=OpenApiParameter.QUERY,
                             description="Filter appointments by stylist name."),
        ],
        responses={
            200: OpenApiResponse(
                description="List of appointments",
                response=AppointmentListSerializer(many=True)
            ),
            400: OpenApiResponse(description="Bad Request"),
            500: OpenApiResponse(description="Internal Server Error")
        }
    )
    def get(self, request, format=None):
        date_param = request.query_params.get('date', None)
        stylist = request.query_params.get('stylist', None)

        try:
            if date_param:
                try:
                    # Convert the string date_param to a datetime.date object
                    appointment_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                except ValueError:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                appointment_date = datetime.today().date()

            # Filter appointments by date and optionally by stylist
            appointments = Appointment.objects.filter(
                date=appointment_date,
                status__in=['scheduled', 'rescheduled']  # Exclude cancelled appointments
            )

            if stylist:
                appointments = appointments.filter(stylist=stylist)

            appointments = appointments.order_by('time')

            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

