# CampusConnect

Welcome to **CampusConnect**, a collaborative Django-based classroom management platform. This repository contains the source code for the platform, which includes multi-file announcements, late assignment handling, attendance tracking, and student/teacher dashboards built with a sleek interface.

## 🚀 Getting Started

Follow these steps to get the project running locally on your machine.

### Prerequisites
- **Python 3.10+** installed on your system.
- **PostgreSQL** installed and running locally (or access to a remote PostgreSQL instance).

### 1. Clone the Repository
```bash
git clone <repo-url>
cd "Agile v5.2"
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example file and fill in your values:
```bash
cp .env.example .env
```
Then edit `.env` and set:
- **`DJANGO_SECRET_KEY`** — Generate one by running:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- **`DATABASE_PASSWORD`** — Your local PostgreSQL password.

That's it — Django loads the `.env` file automatically.

### 5. Create the Database
Make sure PostgreSQL is running, then create the database:
```sql
CREATE DATABASE agile_classroom;
```

### 6. Apply Database Migrations
```bash
cd core
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser (Admin)
To test the Teacher views or access the Django admin panel:
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📁 Key Directories

- `main/` - Core routing, models for Classrooms/Users, and Dashboard logic.
- `assignments/` - Assignment creation, management, and multiple file attachments.
- `submissions/` - Student submission logic handling late files, grading, and resubmissions.
- `attendance/` - Teacher dashboard tools for attendance checking.
- `cia/` - Continuous Internal Assessment records.
- `resources/` - Shared classroom resources and file management.
- `templates/` - Our fully-styled HTML templates using Bootstrap 5.

