# 🚀 Quick Start: Get Notifications Working in 3 Steps

## Step 1: Restart Backend Server ⚡

```bash
# Stop current server (Ctrl+C in the terminal)
# Then run:
cd backend
python manage.py runserver
```

**Wait for**: `Starting development server at http://127.0.0.1:8000/`

---

## Step 2: Refresh Your Login 🔄

1. Open frontend: http://localhost:3000
2. **Log out** (click profile → Logout)
3. **Log back in** with your credentials

---

## Step 3: Test It! 🧪

### Quick Test (30 seconds):

1. **Open browser console** (Press F12)
2. **Paste this code** and press Enter:
   ```javascript
   fetch('http://127.0.0.1:8000/api/notifications/test/', {
     method: 'POST',
     headers: {
       'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
       'Content-Type': 'application/json'
     }
   }).then(r => r.json()).then(console.log)
   ```
3. **Refresh the page** (F5)
4. **Click the bell icon** (top right corner)
5. **You should see a test notification!** 🎉

### Real Test (2 minutes):

**As Patient:**
1. Go to "Available Doctors"
2. Book an appointment
3. Log in as doctor
4. Check notification bell → You'll see "New Appointment Booked"

**As Doctor:**
1. Go to "Doctor Panel"
2. Confirm an appointment
3. Log in as that patient
4. Check notification bell → You'll see "Appointment Confirmed"

---

## ✅ Success Checklist

- [ ] Backend server restarted
- [ ] Logged out and back in
- [ ] Test notification created
- [ ] Red dot appears on bell icon
- [ ] Clicking bell shows notifications
- [ ] Notifications have proper content

---

## 🎯 What You'll See

### Notification Bell (Top Right)
```
🔔 ← Click this
 ● ← Red dot = unread notifications
```

### Notification Dropdown
```
┌─────────────────────────────────┐
│ Notifications    Mark all read  │
├─────────────────────────────────┤
│ ● New Appointment Booked        │
│   John Doe has booked...        │
│   2 minutes ago                 │
├─────────────────────────────────┤
│   Appointment Confirmed         │
│   Your appointment with...      │
│   1 hour ago                    │
├─────────────────────────────────┤
│        View all notifications   │
└─────────────────────────────────┘
```

---

## 🐛 Not Working?

### Check 1: Is backend running?
```bash
# Should show: System check identified no issues
cd backend
python manage.py check
```

### Check 2: Are notifications in database?
```bash
cd backend
python verify_notification_system.py
```

### Check 3: Any errors in browser?
- Press F12
- Look at Console tab
- Look for red error messages

### Check 4: Fresh tokens?
- Log out completely
- Close all browser tabs
- Open new tab
- Log back in

---

## 📋 Notification Types

| When | Who Gets Notified |
|------|-------------------|
| Patient books appointment | Doctor |
| Doctor confirms appointment | Patient |
| Doctor issues prescription | Patient |
| Appointment cancelled | Other party |
| Appointment completed | Patient |
| Patient submits review | Doctor |

---

## 💡 Pro Tips

1. **Notifications are real-time** - they appear immediately after actions
2. **Click a notification** to go to the relevant page
3. **Red dot** shows unread count
4. **Mark all as read** clears all unread at once
5. **Notifications persist** - they don't disappear until you mark them read

---

## 🎉 That's It!

Your notification system is now fully operational. Every patient-doctor interaction will automatically create appropriate notifications.

**Need more details?** See `NOTIFICATION_STATUS.md` for comprehensive documentation.

---

**Remember**: The #1 issue is forgetting to restart the backend server! 🔄
