# Notification System Implementation

## Overview
Comprehensive notification system that automatically creates notifications for key actions between patients and doctors.

## Notification Types

### 1. **Appointment Booked** (Doctor receives)
- **Trigger**: When a patient books a new appointment
- **Recipient**: Doctor
- **Message**: "{Patient Name} has booked an appointment with you on {Date} at {Time}. Reason: {Reason}"

### 2. **Appointment Confirmed** (Patient receives)
- **Trigger**: When doctor confirms an appointment
- **Recipient**: Patient
- **Message**: "Your appointment with {Doctor Name} on {Date} at {Time} has been confirmed."

### 3. **Appointment Cancelled** (Both parties)
- **Trigger**: When either party cancels an appointment
- **Recipient**: The other party (patient or doctor)
- **Message**: 
  - To Doctor: "{Patient Name} has cancelled their appointment scheduled for {Date} at {Time}."
  - To Patient: "Your appointment with {Doctor Name} on {Date} at {Time} has been cancelled."

### 4. **Appointment Completed** (Patient receives)
- **Trigger**: When doctor marks appointment as completed
- **Recipient**: Patient
- **Message**: "Your appointment with {Doctor Name} has been completed. You can now view your prescription and medical records."

### 5. **Prescription Issued** (Patient receives)
- **Trigger**: When doctor creates a prescription
- **Recipient**: Patient
- **Message**: "{Doctor Name} has issued a prescription for your appointment on {Date}. You can view it in the Prescriptions section."

### 6. **Payment Received** (Doctor receives)
- **Trigger**: When payment is processed
- **Recipient**: Doctor
- **Message**: "Payment of ${Amount} has been received from {Patient Name} for the appointment on {Date}."

### 7. **Review Submitted** (Doctor receives)
- **Trigger**: When patient submits a review
- **Recipient**: Doctor
- **Message**: "{Patient Name} has left a {Rating}-star review for you: \"{Comment preview}\""

### 8. **Appointment Reminder** (Patient receives)
- **Trigger**: 24 hours before appointment (requires scheduled task)
- **Recipient**: Patient
- **Message**: "Reminder: You have an appointment with {Doctor Name} tomorrow at {Time}. Please arrive 10 minutes early."

## Implementation Details

### Backend Components

1. **NotificationService** (`notifications/services.py`)
   - Centralized service for creating notifications
   - Methods for each notification type
   - Handles message formatting and recipient determination

2. **Integration Points**
   - `appointments/views.py`: Appointment booking, status updates, prescription creation
   - `reviews/views.py`: Review submission
   - `payments/views.py`: Payment processing (ready for integration)

### Notification Flow

```
User Action → View Method → NotificationService → Notification Created → User Receives Notification
```

### Example Usage

```python
from notifications.services import NotificationService

# When patient books appointment
appointment = serializer.save(patient=request.user)
NotificationService.notify_appointment_booked(appointment)

# When doctor confirms appointment
if new_status == 'confirmed':
    NotificationService.notify_appointment_confirmed(appointment)

# When doctor issues prescription
NotificationService.notify_prescription_issued(appointment)
```

## Features

✅ **Automatic Notifications**: No manual intervention required
✅ **Role-Based**: Notifications sent to appropriate party (patient/doctor)
✅ **Context-Aware**: Messages include relevant details (names, dates, times)
✅ **Action-Triggered**: Real-time notifications on key events
✅ **Comprehensive Coverage**: All major patient-doctor interactions

## Future Enhancements

- Email notifications
- SMS notifications
- Push notifications
- Notification preferences (user can enable/disable specific types)
- Scheduled reminders (appointment reminders 24h before)
- Read receipts
- Notification grouping
