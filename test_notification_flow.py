#!/usr/bin/env python
"""
Comprehensive Notification System Test
Tests the entire notification flow from creation to API retrieval
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from notifications.models import Notification
from notifications.services import NotificationService
from users.models import User
from doctors.models import Doctor
from appointments.models import Appointment
from datetime import date, time

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_notification_database():
    """Test 1: Check if notifications exist in database"""
    print_section("TEST 1: Database Check")
    
    total = Notification.objects.count()
    print(f"✓ Total notifications in database: {total}")
    
    if total > 0:
        print("\nRecent notifications:")
        for notif in Notification.objects.all()[:5]:
            status = "✓ Read" if notif.is_read else "○ Unread"
            print(f"  {status} | {notif.user.username} | {notif.title}")
            print(f"           {notif.message[:80]}...")
            print(f"           Created: {notif.created_at}")
    else:
        print("⚠ No notifications found in database")
    
    return total > 0

def test_notification_service():
    """Test 2: Test NotificationService can create notifications"""
    print_section("TEST 2: NotificationService Test")
    
    try:
        # Get a test user
        user = User.objects.filter(role='patient').first()
        if not user:
            print("⚠ No patient user found to test with")
            return False
        
        print(f"✓ Found test user: {user.username}")
        
        # Create a test notification
        notification = NotificationService.create_notification(
            user=user,
            title="System Test Notification",
            message="This is a test notification created by the test script."
        )
        
        print(f"✓ Created notification ID: {notification.id}")
        print(f"  Title: {notification.title}")
        print(f"  User: {notification.user.username}")
        print(f"  Created: {notification.created_at}")
        
        # Verify it was saved
        saved = Notification.objects.filter(id=notification.id).exists()
        if saved:
            print("✓ Notification successfully saved to database")
        else:
            print("✗ Notification NOT found in database")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error creating notification: {e}")
        return False

def test_appointment_notification():
    """Test 3: Test appointment booking notification"""
    print_section("TEST 3: Appointment Notification Test")
    
    try:
        # Get a patient and doctor
        patient = User.objects.filter(role='patient').first()
        doctor_profile = Doctor.objects.first()
        
        if not patient or not doctor_profile:
            print("⚠ Need both patient and doctor to test")
            return False
        
        print(f"✓ Patient: {patient.username}")
        print(f"✓ Doctor: {doctor_profile.user.username}")
        
        # Check if there's an existing appointment
        appointment = Appointment.objects.filter(
            patient=patient,
            doctor=doctor_profile
        ).first()
        
        if appointment:
            print(f"✓ Found existing appointment ID: {appointment.id}")
            print(f"  Status: {appointment.status}")
            print(f"  Date: {appointment.appointment_date}")
            
            # Test notification creation
            old_count = Notification.objects.filter(user=doctor_profile.user).count()
            NotificationService.notify_appointment_booked(appointment)
            new_count = Notification.objects.filter(user=doctor_profile.user).count()
            
            if new_count > old_count:
                print(f"✓ Notification created for doctor")
                latest = Notification.objects.filter(user=doctor_profile.user).latest('created_at')
                print(f"  Title: {latest.title}")
                print(f"  Message: {latest.message[:80]}...")
                return True
            else:
                print("⚠ Notification count did not increase")
                return False
        else:
            print("⚠ No appointments found to test with")
            return False
            
    except Exception as e:
        print(f"✗ Error testing appointment notification: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_serialization():
    """Test 4: Test notification serialization for API"""
    print_section("TEST 4: API Serialization Test")
    
    try:
        from notifications.serializers import NotificationSerializer
        
        notification = Notification.objects.first()
        if not notification:
            print("⚠ No notifications to serialize")
            return False
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        print("✓ Serialized notification data:")
        print(f"  ID: {data.get('id')}")
        print(f"  User: {data.get('user')}")
        print(f"  Title: {data.get('title')}")
        print(f"  Message: {data.get('message')[:80]}...")
        print(f"  Is Read: {data.get('is_read')}")
        print(f"  Created At: {data.get('created_at')}")
        
        # Check all required fields are present
        required_fields = ['id', 'user', 'title', 'message', 'is_read', 'created_at']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            print(f"✗ Missing fields: {missing}")
            return False
        else:
            print("✓ All required fields present")
            return True
            
    except Exception as e:
        print(f"✗ Error serializing notification: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_notifications():
    """Test 5: Test getting notifications for specific users"""
    print_section("TEST 5: User Notifications Test")
    
    try:
        # Test for each user type
        for role in ['patient', 'doctor']:
            user = User.objects.filter(role=role).first()
            if not user:
                print(f"⚠ No {role} user found")
                continue
            
            notifications = Notification.objects.filter(user=user)
            count = notifications.count()
            
            print(f"\n{role.upper()}: {user.username}")
            print(f"  Total notifications: {count}")
            
            if count > 0:
                unread = notifications.filter(is_read=False).count()
                print(f"  Unread: {unread}")
                print(f"  Recent notifications:")
                for notif in notifications[:3]:
                    status = "○" if not notif.is_read else "✓"
                    print(f"    {status} {notif.title}")
            else:
                print(f"  ⚠ No notifications for this user")
        
        return True
        
    except Exception as e:
        print(f"✗ Error getting user notifications: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  NOTIFICATION SYSTEM COMPREHENSIVE TEST")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Database Check", test_notification_database()))
    results.append(("NotificationService", test_notification_service()))
    results.append(("Appointment Notification", test_appointment_notification()))
    results.append(("API Serialization", test_api_serialization()))
    results.append(("User Notifications", test_user_notifications()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Notification system is working correctly.")
        print("\nNext steps:")
        print("1. Make sure backend server is running: python manage.py runserver")
        print("2. Log out and log back in to the frontend")
        print("3. Try booking an appointment or confirming one")
        print("4. Check the notification bell in the top right corner")
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
