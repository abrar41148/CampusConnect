# Test Cases (High‑Level)

## Scope
Cover core functionality across unit, integration, and acceptance levels for the CampusConnect system.

## Unit Test Areas
- **Models**: Validation, string representations, relationship integrity.
- **Views**: Permission checks, correct template rendering, context data.
- **Forms**: Field validation, error messages.

## Integration Test Scenarios
| Scenario | Description |
|----------|-------------|
| User Registration & Login | Verify that a new user can register, receive confirmation, and log in with correct role. |
| Classroom CRUD | Teacher creates a classroom, edits details, and deletes it; ensure enrollment updates accordingly. |
| Enrollment Flow | Student joins a classroom, sees it on dashboard, and can leave; verify enrollment records. |
| Assignment Lifecycle | Teacher creates an assignment, student views it, submits before deadline, teacher grades. |
| Announcement Visibility | Teacher posts announcement; enrolled students see it, others do not. |

## Acceptance Test Checklist (aligned with user stories)
- **Student** can register, log in, view/join classrooms, see assignments, submit work, receive announcements.
- **Teacher** can manage classrooms, post announcements, create/edit assignments, review submissions.
- **Admin** can manage users, view system metrics, configure settings.

## Non‑Functional Tests
- **Performance**: Page load time < 2 s for dashboard under typical load.
- **Security**: Access control enforced; CSRF tokens present.
- **Usability**: UI renders correctly in dark mode on desktop and mobile.

*Tests will be implemented using Django’s test framework and pytest for richer assertions.*
