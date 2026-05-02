# Sprint Planning (High‑Level)

## Sprint Structure
- **Sprint Length**: 2 weeks per sprint (typical Agile cadence).
- **Total Sprints**: 4 sprints to cover core functionality and polish.

## Sprint Goals & Backlog Overview
| Sprint | Goal | Representative Backlog Items (high‑level) |
|--------|------|-------------------------------------------|
| 1 | **Foundations** – Set up project scaffolding, authentication, and basic UI. | • Implement user registration & login (Student, Teacher, Admin).<br>• Create core models: User, Classroom, Enrollment.<br>• Basic dashboard UI for each role. |
| 2 | **Classroom & Enrollment** – Enable classroom management and student enrollment. | • CRUD for Classroom (create, edit, delete).<br>• Enrollment flow (students join/leave classrooms).<br>• Announcements list view. |
| 3 | **Assignments & Submissions** – Provide assignment lifecycle and submission handling. | • Assignment creation/editing by teachers.<br>• Student view of upcoming assignments.<br>• Submission upload and deadline enforcement.<br>• Teacher grading UI (placeholder). |
| 4 | **Polish & Release** – Refine UI/UX, add tests, and prepare for production. | • Dark‑mode enhancements, micro‑animations.<br>• Comprehensive test suite (unit, integration).<br>• Documentation finalization.<br>• Deployment scripts (Docker). |

## Definition of Done (DoD) per Sprint
- Code merged to `main` with peer review.
- Unit tests ≥ 80% coverage for affected modules.
- UI passes manual accessibility checklist.
- Updated documentation reflects new features.

---
*This high‑level plan can be refined into detailed tickets as needed.*
