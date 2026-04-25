# Backend Setup Instructions

## Prerequisites
- Python 3.10+
- PostgreSQL installed and running on port 5050
- Database named `Doctorapp_db` created

## Setup Steps

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your database password:
```
DB_PASSWORD=your_postgres_password
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

The API will be available at http://localhost:8000

## API Endpoints

### Authentication
- POST /api/auth/register/ - Register new user
- POST /api/auth/login/ - Login (returns JWT tokens)
- POST /api/auth/token/refresh/ - Refresh access token
- GET /api/auth/profile/ - Get user profile

### Doctors
- GET /api/doctors/ - List all doctors
- GET /api/doctors/{id}/ - Get doctor details

### Appointments
- GET /api/appointments/ - List user appointments
- POST /api/appointments/ - Create appointment
- GET /api/appointments/{id}/ - Get appointment details
- PUT /api/appointments/{id}/ - Update appointment
- DELETE /api/appointments/{id}/ - Cancel appointment

### Reviews
- GET /api/reviews/ - List reviews
- POST /api/reviews/ - Create review

### Payments
- GET /api/payments/ - List payments

### Notifications
- GET /api/notifications/ - List notifications
