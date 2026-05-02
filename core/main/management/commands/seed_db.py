"""
Management command to wipe the database and populate it with realistic
dummy data so the app looks like it has been actively used for a semester.

Usage:
    python manage.py seed_db
"""

import random
from datetime import timedelta, time, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from main.models import Profile, Classroom, ClassroomMembership, Alert
from assignments.models import Assignment
from submissions.models import Submission
from attendance.models import AttendanceSession, Attendance
from resources.models import Resource
from cia.models import CIARecord


# ──────────────────────────── helpers ────────────────────────────

def past(days_ago, hour=10, minute=0):
    """Return an aware datetime `days_ago` days in the past."""
    return timezone.now() - timedelta(days=days_ago) + timedelta(
        hours=hour - timezone.now().hour,
        minutes=minute - timezone.now().minute,
    )


def random_past(min_days=1, max_days=90):
    return timezone.now() - timedelta(
        days=random.randint(min_days, max_days),
        hours=random.randint(0, 12),
        minutes=random.randint(0, 59),
    )


# ──────────────────────────── data pools ─────────────────────────

TEACHER_DATA = [
    {"first": "Rajesh",   "last": "Kumar",       "username": "Dr Rajesh Kumar",   "email": "rajesh.kumar@campus.edu"},
    {"first": "Priya",    "last": "Sharma",       "username": "Dr Priya Sharma",   "email": "priya.sharma@campus.edu"},
    {"first": "Anil",     "last": "Mehta",        "username": "Prof Anil Mehta",   "email": "anil.mehta@campus.edu"},
    {"first": "Sunita",   "last": "Iyer",         "username": "Dr Sunita Iyer",    "email": "sunita.iyer@campus.edu"},
]

STUDENT_DATA = [
    {"first": "Aarav",    "last": "Patel",    "sec": "A"},
    {"first": "Vivaan",   "last": "Singh",    "sec": "A"},
    {"first": "Aditya",   "last": "Reddy",    "sec": "A"},
    {"first": "Ananya",   "last": "Nair",     "sec": "A"},
    {"first": "Diya",     "last": "Gupta",    "sec": "A"},
    {"first": "Ishaan",   "last": "Joshi",    "sec": "B"},
    {"first": "Kavya",    "last": "Rao",      "sec": "B"},
    {"first": "Rohan",    "last": "Chopra",   "sec": "B"},
    {"first": "Meera",    "last": "Das",      "sec": "B"},
    {"first": "Arjun",    "last": "Bhat",     "sec": "B"},
    {"first": "Sanya",    "last": "Verma",    "sec": "A"},
    {"first": "Tanvi",    "last": "Deshmukh", "sec": "A"},
    {"first": "Nikhil",   "last": "Kulkarni", "sec": "B"},
    {"first": "Pooja",    "last": "Menon",    "sec": "A"},
    {"first": "Rahul",    "last": "Pillai",   "sec": "B"},
    {"first": "Sneha",    "last": "Thakur",   "sec": "A"},
    {"first": "Varun",    "last": "Saxena",   "sec": "B"},
    {"first": "Kriti",    "last": "Agarwal",  "sec": "A"},
    {"first": "Dev",      "last": "Chauhan",  "sec": "B"},
    {"first": "Nisha",    "last": "Banerjee", "sec": "A"},
]

CLASSROOM_DATA = [
    {"name": "CS3101 - Data Structures & Algorithms",  "teacher_idx": 0},
    {"name": "CS3202 - Database Management Systems",    "teacher_idx": 0},
    {"name": "CS3303 - Operating Systems",              "teacher_idx": 1},
    {"name": "MA2101 - Discrete Mathematics",           "teacher_idx": 2},
    {"name": "CS3404 - Computer Networks",              "teacher_idx": 1},
    {"name": "CS3505 - Software Engineering",           "teacher_idx": 3},
]

# Realistic assignment titles per classroom index
ASSIGNMENT_POOL = {
    0: [  # DSA
        ("Implement a Binary Search Tree", "Write a complete BST implementation in Python with insert, delete, search, and traversal methods. Include time-complexity analysis for each operation.", 100),
        ("Sorting Algorithms Comparison", "Implement Merge Sort, Quick Sort, and Heap Sort. Benchmark their performance on arrays of size 1K, 10K, and 100K. Present results in a table.", 50),
        ("Graph Traversal – BFS & DFS", "Implement BFS and DFS for an adjacency-list representation. Demonstrate on a sample graph of at least 10 nodes. Identify connected components.", 100),
        ("Dynamic Programming Problem Set", "Solve the following DP problems: Longest Common Subsequence, 0/1 Knapsack, and Matrix Chain Multiplication. Show state-transition tables.", 75),
        ("Hash Table with Chaining", "Build a hash table that handles collisions via chaining. Support insert, delete, and lookup. Analyse load factor impact on performance.", 50),
    ],
    1: [  # DBMS
        ("ER Diagram for Library System", "Design a complete ER diagram for a university library management system. Include at least 6 entities with proper relationships and cardinality.", 100),
        ("SQL Joins & Subqueries", "Write SQL queries using INNER JOIN, LEFT JOIN, and correlated subqueries to answer 10 business questions on the provided schema.", 50),
        ("Normalisation to 3NF", "Take the provided un-normalised table and step through 1NF → 2NF → 3NF. Show functional dependencies at each stage.", 75),
        ("PL/SQL Stored Procedures", "Create stored procedures for: adding a new student, enrolling in a course, calculating GPA, and generating a transcript.", 100),
    ],
    2: [  # OS
        ("Process Scheduling Simulation", "Simulate FCFS, SJF, and Round Robin scheduling. Accept process arrival & burst times as input. Output Gantt charts and average waiting/turnaround times.", 100),
        ("Page Replacement Algorithms", "Implement FIFO, LRU, and Optimal page replacement. Test with a reference string of 20+ pages and compare page-fault rates.", 75),
        ("Producer-Consumer Problem", "Implement the bounded-buffer producer-consumer problem using semaphores/mutexes in C or Python. Demonstrate with 3 producers and 2 consumers.", 50),
        ("File System Design Document", "Design a simple file system supporting hierarchical directories, file creation/deletion, and basic permissions. Submit a design document with diagrams.", 100),
    ],
    3: [  # Discrete Math
        ("Proof by Induction Problem Set", "Prove the following 5 statements using mathematical induction. Show the base case and inductive step clearly for each.", 50),
        ("Graph Theory Exercises", "Solve problems on Euler/Hamilton paths, graph colouring, and planarity. Include diagrams for each solution.", 75),
        ("Combinatorics & Counting", "Solve 10 problems on permutations, combinations, pigeonhole principle, and inclusion-exclusion. Show all working.", 50),
        ("Boolean Algebra Simplification", "Simplify the given 8 Boolean expressions using algebraic laws and verify with truth tables. Implement the simplified circuits.", 75),
    ],
    4: [  # Networks
        ("Socket Programming – Chat App", "Build a simple TCP chat application in Python with a server handling multiple clients. Include username support and broadcast messaging.", 100),
        ("Wireshark Packet Analysis", "Capture HTTP, DNS, and TCP traffic using Wireshark. Analyse 3 packet captures and answer the provided questions about protocol behaviour.", 75),
        ("Subnetting Exercise Set", "Given 5 network scenarios, perform subnetting: calculate subnet masks, host ranges, and broadcast addresses. Show all binary calculations.", 50),
        ("HTTP Server from Scratch", "Implement a basic HTTP/1.1 server in Python that serves static files, handles GET/POST, and returns proper status codes (200, 404, 500).", 100),
    ],
    5: [  # SE
        ("Software Requirements Specification", "Write an SRS document (IEEE 830 format) for an online food-delivery platform. Include functional & non-functional requirements, use cases, and UML diagrams.", 100),
        ("Design Patterns Implementation", "Implement Singleton, Observer, and Factory patterns in Python/Java. Provide a real-world use case and UML class diagram for each.", 75),
        ("Agile Sprint Retrospective", "Conduct a retrospective on the class project sprint. Document what went well, what didn't, and action items. Include velocity charts.", 50),
        ("Unit Testing & Code Coverage", "Write unit tests for the provided codebase achieving ≥85% coverage. Use pytest/JUnit. Submit the test suite and coverage report.", 75),
        ("CI/CD Pipeline Setup", "Set up a GitHub Actions CI/CD pipeline for a sample project. Include linting, testing, building, and deployment stages. Document with screenshots.", 100),
    ],
}

ANNOUNCEMENT_POOL = [
    ("Welcome to the class!", "Hello everyone! Welcome to this semester's class. Please make sure you have access to all the required materials. Looking forward to a great semester together."),
    ("Mid-semester exam schedule", "The mid-semester examination is scheduled for the week of March 10–14. The detailed seating arrangement will be shared by next week. Please start your revision early."),
    ("Guest lecture next week", "We will have a guest lecture by an industry professional next Wednesday at 2:00 PM. Attendance is mandatory. The topic will be announced shortly."),
    ("Assignment submission guidelines", "A reminder that all assignments must be submitted via CampusConnect before the deadline. Late submissions will be penalized as per the syllabus. No email submissions accepted."),
    ("Lab session rescheduled", "Due to a faculty meeting, this week's lab session has been moved from Thursday to Friday, same time and venue. Please update your calendars."),
    ("Important: Academic integrity", "Please review the academic integrity policy. Any form of plagiarism will result in zero marks for the assignment and may lead to disciplinary action."),
    ("Study material uploaded", "I've uploaded additional reference PDFs and solved examples in the Materials section. These cover the topics we discussed this week and will be helpful for the upcoming test."),
    ("Project team formation", "Please form your project teams (3–4 members) and register your team via the form shared on the class notice board by this Friday."),
    ("Class cancelled tomorrow", "Tomorrow's lecture is cancelled due to unforeseen circumstances. The makeup class will be held on Saturday at 10:00 AM. Apologies for the inconvenience."),
    ("End-semester exam prep", "I've uploaded a set of previous year question papers in the Materials section. I strongly recommend solving them under timed conditions for best preparation."),
    ("Feedback form", "Please take a moment to fill out the anonymous course feedback form. Your feedback helps us improve the course for future batches."),
    ("Holiday notice", "Please note that there will be no classes on Monday and Tuesday next week due to the university festival. Classes resume on Wednesday as usual."),
]

FEEDBACK_POOL = [
    "Great work! Clean code and well-documented.",
    "Good effort, but watch out for edge cases.",
    "Needs improvement. Review the lecture slides on this topic.",
    "Excellent submission! One of the best in the class.",
    "Correct approach, but the code could be more efficient.",
    "Well-structured report. Minor formatting issues.",
    "Late submission noted. Content quality is good though.",
    "Incomplete solution. Please review the requirements.",
    "Solid work overall. Minor deductions for output formatting.",
    "Very thorough analysis. Keep it up!",
    "Good attempt. Revisit the time-complexity section.",
    "Perfect score. Outstanding work!",
]


# ──────────────────────────── command ────────────────────────────

class Command(BaseCommand):
    help = "Wipe the database and populate with realistic dummy data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("[*] Clearing existing data..."))
        self._clear()
        self.stdout.write(self.style.SUCCESS("[OK] Database cleared."))

        self.stdout.write("[*] Creating teachers...")
        teachers = self._create_teachers()

        self.stdout.write("[*] Creating students...")
        students = self._create_students()

        self.stdout.write("[*] Creating classrooms & enrollments...")
        classrooms = self._create_classrooms(teachers, students)

        self.stdout.write("[*] Creating assignments & submissions...")
        self._create_assignments_and_submissions(classrooms, teachers, students)

        self.stdout.write("[*] Creating attendance history...")
        self._create_attendance(classrooms, students)

        self.stdout.write("[*] Creating announcements...")
        self._create_announcements(classrooms, teachers)

        self.stdout.write("[*] Creating CIA records...")
        self._create_cia_records(classrooms, students)

        self.stdout.write("[*] Creating alerts...")
        self._create_alerts(students, teachers)

        self.stdout.write(self.style.SUCCESS(
            "\n[DONE] Database seeded successfully! The app now looks well-used."
        ))
        self.stdout.write(self.style.SUCCESS(
            "   Login credentials: all passwords are 'campus123'"
        ))

    # ── clear ──

    def _clear(self):
        Alert.objects.all().delete()
        CIARecord.objects.all().delete()
        Attendance.objects.all().delete()
        AttendanceSession.objects.all().delete()
        Submission.objects.all().delete()
        Assignment.objects.all().delete()
        Resource.objects.all().delete()
        ClassroomMembership.objects.all().delete()
        Classroom.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()

    # ── teachers ──

    def _create_teachers(self):
        teachers = []
        for td in TEACHER_DATA:
            u = User.objects.create_user(
                username=td["username"],
                password="campus123",
                first_name=td["first"],
                last_name=td["last"],
                email=td["email"],
            )
            # Profile auto-created by signal; update role
            u.profile.role = "teacher"
            u.profile.save()
            teachers.append(u)
            self.stdout.write(f"   + {u.username}")
        return teachers

    # ── students ──

    def _create_students(self):
        students = []
        for sd in STUDENT_DATA:
            uname = f"{sd['first']} {sd['last']}"
            u = User.objects.create_user(
                username=uname,
                password="campus123",
                first_name=sd["first"],
                last_name=sd["last"],
                email=f"{sd['first'].lower()}.{sd['last'].lower()}@student.campus.edu",
            )
            u.profile.role = "student"
            u.profile.section = sd["sec"]
            u.profile.save()
            students.append(u)
        self.stdout.write(f"   + Created {len(students)} students")
        return students

    # ── classrooms ──

    def _create_classrooms(self, teachers, students):
        classrooms = []
        for cd in CLASSROOM_DATA:
            teacher = teachers[cd["teacher_idx"]]
            c = Classroom.objects.create(name=cd["name"], teacher=teacher)

            # enrol a realistic subset of students (12-18 per class)
            enrolled = random.sample(students, k=random.randint(12, min(18, len(students))))
            for s in enrolled:
                c.students.add(s)
                ClassroomMembership.objects.create(classroom=c, student=s)

            # occasionally add a co-teacher
            other_teachers = [t for t in teachers if t != teacher]
            if random.random() > 0.5 and other_teachers:
                co = random.choice(other_teachers)
                c.teachers.add(co)

            classrooms.append(c)
            self.stdout.write(f"   + {c.name}  ({len(enrolled)} students, code: {c.join_code})")
        return classrooms

    # ── assignments & submissions ──

    def _create_assignments_and_submissions(self, classrooms, teachers, students):
        for idx, classroom in enumerate(classrooms):
            pool = ASSIGNMENT_POOL.get(idx, ASSIGNMENT_POOL[0])
            teacher = classroom.teacher
            enrolled = list(classroom.students.all())

            for a_idx, (title, desc, max_g) in enumerate(pool):
                # Stagger deadlines: oldest assignment ~80 days ago, newest ~3 days ahead
                total = len(pool)
                days_offset = int(80 - (a_idx / max(total - 1, 1)) * 83)  # +80 → -3
                deadline = timezone.now() - timedelta(days=days_offset)

                # Use update to bypass auto_now_add for created_at
                a = Assignment.objects.create(
                    title=title,
                    description=desc,
                    deadline=deadline,
                    classroom=classroom,
                    created_by=teacher,
                    max_grade=max_g,
                    allow_late_submissions=random.choice([True, True, True, False]),
                )
                # Backdate created_at to ~3 days before deadline
                Assignment.objects.filter(pk=a.pk).update(
                    created_at=deadline - timedelta(days=random.randint(3, 7))
                )

                # Only create submissions for past-deadline assignments
                if deadline < timezone.now():
                    for student in enrolled:
                        # 85% submission rate
                        if random.random() < 0.85:
                            is_late = random.random() < 0.15
                            sub_time = deadline + timedelta(
                                hours=random.randint(1, 48)
                            ) if is_late else deadline - timedelta(
                                hours=random.randint(1, 72)
                            )

                            sub = Submission.objects.create(
                                assignment=a,
                                student=student,
                                is_late=is_late,
                            )
                            Submission.objects.filter(pk=sub.pk).update(
                                submitted_at=sub_time,
                            )

                            # 70% graded for past assignments
                            if random.random() < 0.70:
                                grade = self._realistic_grade(max_g, is_late)
                                fb = random.choice(FEEDBACK_POOL) if random.random() < 0.6 else ""
                                Submission.objects.filter(pk=sub.pk).update(
                                    grade=grade,
                                    graded_by=teacher,
                                    feedback=fb,
                                )

            self.stdout.write(f"   + {classroom.name}: {len(pool)} assignments")

    def _realistic_grade(self, max_grade, is_late):
        """Generate a grade that follows a semi-realistic distribution."""
        if is_late:
            pct = random.gauss(0.65, 0.15)
        else:
            pct = random.gauss(0.78, 0.12)
        pct = max(0.20, min(1.0, pct))
        return round(pct * max_grade)

    # ── attendance ──

    def _create_attendance(self, classrooms, students):
        for classroom in classrooms:
            enrolled = list(classroom.students.all())
            teacher = classroom.teacher

            # Generate ~20-30 sessions over the past 90 days (≈ twice a week)
            num_sessions = random.randint(20, 30)
            session_dates = sorted(random.sample(
                [date.today() - timedelta(days=d) for d in range(1, 91)],
                k=min(num_sessions, 90),
            ))

            for sd in session_dates:
                start_h = random.choice([9, 10, 11, 14, 15])
                session = AttendanceSession.objects.create(
                    classroom=classroom,
                    date=sd,
                    start_time=time(start_h, 0),
                    end_time=time(start_h + 1, 0),
                    recorded_by=teacher,
                )

                for student in enrolled:
                    # ~82% attendance rate
                    status = "Present" if random.random() < 0.82 else "Absent"
                    Attendance.objects.create(
                        session=session,
                        student=student,
                        status=status,
                    )

            self.stdout.write(f"   + {classroom.name}: {len(session_dates)} sessions")

    # ── announcements (resources with no file = announcements) ──

    def _create_announcements(self, classrooms, teachers):
        for classroom in classrooms:
            teacher = classroom.teacher
            # 3-5 announcements per class, spread over the semester
            num = random.randint(3, 5)
            chosen = random.sample(ANNOUNCEMENT_POOL, k=num)
            for title, content in chosen:
                r = Resource.objects.create(
                    title=title,
                    content=content,
                    classroom=classroom,
                    uploaded_by=teacher,
                )
                # Backdate
                Resource.objects.filter(pk=r.pk).update(
                    uploaded_at=random_past(5, 80)
                )
            self.stdout.write(f"   + {classroom.name}: {num} announcements")

    # ── CIA records ──

    def _create_cia_records(self, classrooms, students):
        cia_types = ["CIA1", "CIA2", "CIA3"]
        for classroom in classrooms:
            enrolled = list(classroom.students.all())
            subject = classroom.name.split(" - ")[1] if " - " in classroom.name else classroom.name

            for cia in cia_types:
                # CIA1 ~75 days ago, CIA2 ~45 days ago, CIA3 ~15 days ago
                days_map = {"CIA1": 75, "CIA2": 45, "CIA3": 15}
                exam_date = date.today() - timedelta(days=days_map[cia])

                # Skip CIA3 for some classes (still upcoming)
                if cia == "CIA3" and random.random() < 0.3:
                    continue

                for student in enrolled:
                    marks = self._realistic_grade(50, is_late=False)
                    CIARecord.objects.create(
                        student=student,
                        classroom=classroom,
                        subject=subject,
                        cia_type=cia,
                        marks=min(marks, 50),
                        date=exam_date,
                    )

            self.stdout.write(f"   + {classroom.name}: CIA records")

    # ── alerts ──

    def _create_alerts(self, students, teachers):
        alert_messages = [
            "New assignment posted in {cls}.",
            "Your submission for '{asgn}' has been graded.",
            "Reminder: '{asgn}' is due tomorrow.",
            "New announcement in {cls}.",
            "Attendance recorded for today's session in {cls}.",
            "CIA1 marks have been published for {cls}.",
            "You have been enrolled in {cls}.",
        ]

        all_users = students + teachers
        for user in all_users:
            # Students get 5-12 alerts, teachers get 3-6
            num = random.randint(5, 12) if hasattr(user, 'profile') and user.profile.role == "student" else random.randint(3, 6)
            classrooms = list(Classroom.objects.filter(students=user)) if user.profile.role == "student" else list(Classroom.objects.filter(teacher=user))

            if not classrooms:
                continue

            for _ in range(num):
                cls = random.choice(classrooms)
                assignments = list(Assignment.objects.filter(classroom=cls))
                asgn_title = random.choice(assignments).title if assignments else "Assignment"
                msg = random.choice(alert_messages).format(cls=cls.name, asgn=asgn_title)

                a = Alert.objects.create(
                    user=user,
                    message=msg,
                    is_read=random.random() < 0.6,
                )
                Alert.objects.filter(pk=a.pk).update(
                    created_at=random_past(1, 60)
                )

        self.stdout.write(f"   + Created alerts for {len(all_users)} users")
