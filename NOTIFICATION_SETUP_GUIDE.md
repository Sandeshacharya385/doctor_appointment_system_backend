# Notification System Setup & Testing Guide

## ✅ System Status

The notification system has been successfully implemented and tested. Notifications are being created in the database.

## 🔧 Setup Steps

### 1. Restart Backend Server

**IMPORTANT**: You must restart the Django server for the changes to take effect.

```bash
cd backend
python manage.py runserver
```

### 2. Test the System

Run the verification script to confirm everything is working:

```bash
cd backend
python verify_notification_system.py
```

## 📱 How to See Notifications in the App

### For Users:

1. **Log out** from the current session
2. **Log back in** with your credentials
3. Click the **notification bell icon** in the top right corner
4. You should see all your notifications

### For Testing:

#### Test as Patient:
1. Log in as a patient (e.g., username: `sandesh`, password: `patient123`)
2. Book a new appointment with a doctor
3. **Expected**: Doctor receives "New Appointment Booked" notification
4. Check your notifications - you should see confirmation when doctor responds

#### Test as Doctor:
1. Log in as a doctor (e.g., username: `drsmith`, password: `doctor123`)
2. Check notifications - you should see appointment bookings
3. Confirm an appointment
4. **Expected**: Patient receives "Appointment Confirmed" notification
5. Issue a prescription
6. **Expected**: Patient receives "Prescription Issued" notification

## 🔔 Notification Types Implemented

| Action | Who Gets Notified | When |
|--------|------------------|------|
| **Appointment Booked** | Doctor | Patient books appointment |
| **Appointment Confirmed** | Patient | Doctor confirms appointment |
| **Appointment Cancelled** | Other Party | Either party cancels |
| **Appointment Completed** | Patient | Doctor marks as completed |
| **Prescription Issued** | Patient | Doctor creates prescription |
| **Review Submitted** | Doctor | Patient leaves review |

## 🐛 Troubleshooting

### Notifications Not Showing?

1. **Check if backend server is running**:
   ```bash
   # Should see: Starting development server at http://127.0.0.1:8000/
   ```

2. **Verify notifications exist in database**:
   ```bash
   cd backend
   python verify_notification_system.py
   ```

3. **Clear browser cache and log out/in**:
   - Log out completely
   - Clear browser cache (Ctrl+Shift+Delete)
   - Log back in

4. **Check browser console for errors**:
   - Press F12 to open developer tools
   - Look for any red errors in the Console tab

### API Endpoint Test

Test the notifications API directly:

```bash
# Get access token (replace with your credentials)
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"sandesh","password":"patient123"}'

# Use the access token to get notifications
curl http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 📊 Current Database Status

Run this to see current notifications:

```bash
cd backend
python manage.py shell -c "from notifications.models import Notification; [print(f'{n.user.username}: {n.title}') for n in Notification.objects.all()[:10]]"
```

## ✨ Features

- ✅ Automatic notification creation on key actions
- ✅ Role-based notifications (patient/doctor)
- ✅ Real-time updates
- ✅ Unread notification indicators
- ✅ Notification history
- ✅ Mark as read functionality
- ✅ Clickable notifications that navigate to relevant pages

## 🚀 Next Steps

1. **Restart the backend server** (most important!)
2. **Log out and log back in** to the frontend
3. **Perform test actions** (book appointment, confirm, etc.)
4. **Check notifications** by clicking the bell icon

## 📝 Notes

- Notifications are stored in the database permanently
- Each user only sees their own notifications
- Notifications can be marked as read
- The red dot indicator shows unread notifications
- Clicking a notification navigates to the relevant page
