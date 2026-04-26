from django.urls import path
from .views import (
    AppointmentListCreateView, AppointmentDetailView,
    PrescriptionCreateUpdateView, PatientPrescriptionsView,
    PatientHistoryView,
)

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment-list'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<int:appointment_id>/prescription/', PrescriptionCreateUpdateView.as_view(), name='prescription'),
    path('my-prescriptions/', PatientPrescriptionsView.as_view(), name='my-prescriptions'),
    path('patient-history/<int:patient_id>/', PatientHistoryView.as_view(), name='patient-history'),
]
