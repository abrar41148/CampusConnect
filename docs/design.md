# Design (High‑Level)

## Architecture Overview
- **Django MVC**: Models (PostgreSQL), Views (class‑based views), Templates (Bootstrap with dark‑mode support).
- **REST API** (optional): For future mobile clients, using Django REST Framework.
- **Authentication**: Django auth with role‑based permissions (Student, Teacher, Admin).
- **Email Service**: External SMTP provider for notifications.
- **Containerisation**: Docker Compose for development and production environments.

## Data Model Summary (Key Entities)
- **User** (username, email, password, role)
- **Classroom** (title, description, teacher → User)
- **Enrollment** (student → User, classroom → Classroom)
- **Assignment** (title, description, due_date, classroom → Classroom)
- **Submission** (assignment → Assignment, student → User, file, timestamp)
- **Announcement** (title, content, classroom → Classroom, posted_by → User)

## UI/UX Guidelines
- **Premium aesthetic**: Dark mode default, vibrant accent colors, smooth micro‑animations.
- **Responsive layout**: Mobile‑first, Bootstrap grid.
- **Consistency**: Unified component library for buttons, cards, forms.
- **Accessibility**: ARIA labels, sufficient contrast.
