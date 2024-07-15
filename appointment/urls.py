from django.urls import path
from .views import ScheduleAppointmentView, RescheduleAppointmentView, CancelAppointmentView, ConfirmAppointmentView

urlpatterns = [
    path('schedule', ScheduleAppointmentView.as_view(), name='schedule-appointment'),
    path('<str:ticket_number>/reschedule', RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
    path('<str:ticket_number>/cancel', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('<str:ticket_number>/confirm', ConfirmAppointmentView.as_view(), name='confirm-appointment'),
]
