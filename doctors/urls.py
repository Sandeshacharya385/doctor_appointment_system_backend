from django.urls import path
from .views import (
    DoctorListView, DoctorDetailView,
    DoctorProfileView, DoctorAvailabilityView,
    DoctorAvailabilityDetailView, DoctorAvailableSlotsView
)

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('profile/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('availability/', DoctorAvailabilityView.as_view(), name='doctor-availability'),
    path('availability/<int:pk>/', DoctorAvailabilityDetailView.as_view(), name='doctor-availability-detail'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:doctor_id>/slots/', DoctorAvailableSlotsView.as_view(), name='doctor-slots'),
]
