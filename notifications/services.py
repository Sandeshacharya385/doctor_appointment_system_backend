from .models import Notification
from users.models import User

class NotificationService:
    """Service for creating notifications for various events"""
    
    @staticmethod
    def create_notification(user, title, message):
        """Create a notification for a specific user"""
        return Notification.objects.create(
            user=user,
            title=title,
            message=message
        )
    
    @staticmethod
    def notify_appointment_booked(appointment):
        """Notify doctor when a patient books an appointment"""
        doctor_user = appointment.doctor.user
        patient_name = f"{appointment.patient.first_name} {appointment.patient.last_name}" if appointment.patient.first_name else appointment.patient.username
        
        NotificationService.create_notification(
            user=doctor_user,
            title="New Appointment Booked",
            message=f"{patient_name} has booked an appointment with you on {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')}. Reason: {appointment.reason}"
        )
    
    @staticmethod
    def notify_appointment_confirmed(appointment):
        """Notify patient when doctor confirms appointment"""
        patient_user = appointment.patient
        doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
        
        NotificationService.create_notification(
            user=patient_user,
            title="Appointment Confirmed",
            message=f"Your appointment with {doctor_name} on {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')} has been confirmed."
        )
    
    @staticmethod
    def notify_appointment_cancelled(appointment, cancelled_by):
        """Notify the other party when appointment is cancelled"""
        if cancelled_by == 'patient':
            # Notify doctor
            doctor_user = appointment.doctor.user
            patient_name = f"{appointment.patient.first_name} {appointment.patient.last_name}" if appointment.patient.first_name else appointment.patient.username
            
            NotificationService.create_notification(
                user=doctor_user,
                title="Appointment Cancelled",
                message=f"{patient_name} has cancelled their appointment scheduled for {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')}."
            )
        else:
            # Notify patient
            patient_user = appointment.patient
            doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
            
            NotificationService.create_notification(
                user=patient_user,
                title="Appointment Cancelled",
                message=f"Your appointment with {doctor_name} on {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')} has been cancelled."
            )
    
    @staticmethod
    def notify_appointment_completed(appointment):
        """Notify patient when appointment is marked as completed"""
        patient_user = appointment.patient
        doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
        
        NotificationService.create_notification(
            user=patient_user,
            title="Appointment Completed",
            message=f"Your appointment with {doctor_name} has been completed. You can now view your prescription and medical records."
        )
    
    @staticmethod
    def notify_prescription_issued(appointment):
        """Notify patient when doctor issues a prescription"""
        patient_user = appointment.patient
        doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
        
        NotificationService.create_notification(
            user=patient_user,
            title="New Prescription Available",
            message=f"{doctor_name} has issued a prescription for your appointment on {appointment.appointment_date.strftime('%B %d, %Y')}. You can view it in the Prescriptions section."
        )
    
    @staticmethod
    def notify_payment_received(payment):
        """Notify doctor when payment is received"""
        doctor_user = payment.appointment.doctor.user
        patient_name = f"{payment.user.first_name} {payment.user.last_name}" if payment.user.first_name else payment.user.username
        
        NotificationService.create_notification(
            user=doctor_user,
            title="Payment Received",
            message=f"Payment of ${payment.amount} has been received from {patient_name} for the appointment on {payment.appointment.appointment_date.strftime('%B %d, %Y')}."
        )
    
    @staticmethod
    def notify_review_submitted(review):
        """Notify doctor when patient submits a review"""
        doctor_user = review.doctor.user
        patient_name = f"{review.patient.first_name} {review.patient.last_name}" if review.patient.first_name else review.patient.username
        
        NotificationService.create_notification(
            user=doctor_user,
            title="New Review Received",
            message=f"{patient_name} has left a {review.rating}-star review for you: \"{review.comment[:100]}{'...' if len(review.comment) > 100 else ''}\""
        )
    
    @staticmethod
    def notify_appointment_reminder(appointment):
        """Send appointment reminder to patient (24 hours before)"""
        patient_user = appointment.patient
        doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
        
        NotificationService.create_notification(
            user=patient_user,
            title="Appointment Reminder",
            message=f"Reminder: You have an appointment with {doctor_name} tomorrow at {appointment.appointment_time.strftime('%I:%M %p')}. Please arrive 10 minutes early."
        )
