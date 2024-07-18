from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<str:ticket_number>/', AppointmentDetailView.as_view(), name='appointment-detail'),
]
