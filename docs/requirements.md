# Requirements (Detailed)

## 1. Introduction
- **Purpose**: Provide a web‑based platform for managing classroom activities, assignments, and announcements.
- **Scope**: Supports three user roles (Student, Teacher, Admin) and covers the full lifecycle from enrollment to grading.
- **Definitions**: *Classroom* – a virtual container for a course; *Assignment* – a task with a deadline; *Announcement* – a message posted by  teacher.
a
## 2. Overall Description
- **Product Perspective**: Built on Django MVC, extending the existing CampusConnect codebase.
- **System Interfaces**:
  - Web UI accessed via modern browsers.
  - PostgreSQL database for persistence.
- **User Characteristics**:
  - Students: view/join classrooms, submit assignments.
  - Teachers: create/manage classrooms, assignments, announcements.
  - Admins: manage users, system settings, monitor health.
- **Constraints**: Must run on Linux containers, use Docker Compose for dev/prod.

## 3. Functional Requirements
| ID | Description |
|----|-------------|
| **FR1** | **User Management** – Register, login, password reset, role‑based access control (Student, Teacher, Admin). |
| **FR2** | **Classroom Management** – Teachers can create, edit, delete classrooms; assign themselves as owner. |
| **FR3** | **Enrollment** – Students can request to join a classroom, teachers approve; students can leave classrooms. |
| **FR4** | **Assignment Lifecycle** – Teachers create/edit assignments with title, description, due date, and optional late‑submission policy; students view upcoming assignments and submit files before the deadline. |
| **FR5** | **Submission Review** – Teachers can view submissions, provide feedback, and assign grades. |
| **FR6** | **Announcements** – Teachers post announcements that appear on enrolled students’ dashboards. |
| **FR7** | **Dashboard** – Role‑specific dashboards showing relevant activities (upcoming assignments, recent announcements, enrollment status). |
| **FR8** | **Notifications** – Automatic email on assignment creation, deadline reminders, and announcement posting. |
| **FR9** | **Reporting** – Basic analytics for teachers (submission count, average grade) and admin (user count, system health). |

## 4. Non‑Functional Requirements
- **Performance**: Page load ≤ 2 seconds under typical load; support up to 10 000 concurrent users.
- **Security**: Role‑based permissions, CSRF protection, password hashing with Argon2, input validation, OWASP Top 10 compliance.
- **Usability**: Responsive design, dark‑mode default, premium visual aesthetics, ARIA accessibility, micro‑animations for interactions.
- **Reliability**: 99.9 % uptime, automated daily backups of the PostgreSQL database.
- **Maintainability**: Clean MVC separation, PEP 8 compliance, unit test coverage ≥ 80 % for new code, CI pipeline with linting.
- **Portability**: Dockerized deployment; works on any Linux host supporting Docker Compose.

## 5. System Interfaces
- **Web Interface**: HTML5, CSS3 (Bootstrap), JavaScript (ES6) – accessed via Chrome/Firefox.
- **API (Future)**: JSON over HTTPS using Django REST Framework.
- **Database**: PostgreSQL 13+, schema defined by Django models.
- **External Services**: SMTP provider for email notifications.

## 6. Assumptions & Dependencies
- Development environment uses Python 3.11 and Django 4.2.
- PostgreSQL is available locally for development and in production.
- Docker and Docker‑Compose are installed on the host machine.
- An external SMTP service (e.g., SendGrid) is configured for email delivery.

---
*This document provides a detailed yet concise specification to guide implementation and testing.*
