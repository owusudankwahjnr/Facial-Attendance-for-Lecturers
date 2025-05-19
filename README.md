# 🎓 Lecturer Attendance System with Face Recognition

This is a Django-based attendance management system for university lecturers. It uses facial recognition to verify lecturer presence during scheduled classes. The system features an admin dashboard, attendance tracking, course and class scheduling, and real-time face authentication via webcam.

---

## 📌 Features

### ✅ Authentication & Authorization
- Custom user model with email-based login.
- Separate roles: Admin, Lecturer.
- Face verification during login.

### 🧠 Face Recognition
- Real-time face authentication via webcam.
- Face training per lecturer using DeepFace or similar.
- Admin control over training images and verification models.

### 📅 Attendance Management
- Schedules linked to specific lecturers, programs, and courses.
- Automatically tracks attendance if lecturer face is recognized.
- Records include timestamps and verification status.

### 📊 Admin Dashboard
- Overview statistics: total lecturers, courses, schedules, attendance records.
- Attendance breakdown by lecturer.
- Attendance chart using Chart.js.
- Detailed attendance table:



### 📁 File Upload & Storage
- Training images and face models stored securely.
- Media, models, and venv directories ignored via `.gitignore`.

---

## 🏗️ Tech Stack

- **Backend:** Django, Django ORM
- **Frontend:** Bootstrap 5, Chart.js
- **Face Recognition:** OpenCV, DeepFace (or similar)
- **Database:** SQLite (default, can switch to PostgreSQL/MySQL)
- **Other:** Django Channels (for real-time updates), Redis (optional), gspread (for future integration with Google Sheets)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv
- Git

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/django-attendance-system.git
cd django-attendance-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## 📂 Project Structure
```
├── accounts/ # Custom user model & authentication
├── attendance/ # Attendance logic & scheduling
├── face_auth/ # Face recognition, training & verification
├── media/ # Uploaded face training images (ignored by Git)
├── models/ # Face model files (ignored by Git)
├── templates/ # HTML templates (Django + Bootstrap)
├── static/ # Static files (CSS, JS)
├── venv/ # Virtual environment (ignored by Git)
├── .gitignore
├── manage.py
└── README.md
```

# Virtual environment
venv/

# Face recognition models & training images
media/
models/

# Bytecode & Python cache
__pycache__/
*.py[cod]




