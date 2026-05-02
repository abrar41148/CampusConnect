from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta

from .models import Classroom, ClassroomMembership, Profile, Alert
from resources.models import Resource, ResourceFile
from submissions.models import Submission
from assignments.models import Assignment


# =========================
# LOGIN
# =========================
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            
            try:
                now = timezone.now()
                # Limit to assignments that passed deadline in the last 7 days to avoid N+1 queries on old assignments
                week_ago = now - timedelta(days=7)
                past_assignments = Assignment.objects.for_student(user).filter(deadline__lt=now, deadline__gte=week_ago)
                for a in past_assignments:
                    time_str = a.deadline.strftime('%I:%M %p on %b %d, %Y')
                    msg = f"Assignment '{a.title}' from '{a.classroom.name}' passed its deadline at {time_str}."
                    # Only create the alert if one with this exact message doesn't already exist for the user
                    if not Alert.objects.filter(user=user, message=msg).exists():
                        Alert.objects.create(user=user, message=msg)
            except Exception as e:
                pass # Don't silently break login if assignment lookup fails on weird edge cases
            
            return redirect("dashboard")

        return render(
            request,
            "auth/login.html",
            {"error": "Invalid username or password"},
        )

    return render(request, "auth/login.html")


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student"},
    )

    # ---------- TEACHER DASHBOARD ----------
    if profile.role == "teacher":
        from django.db.models import Q
        classrooms = (
            Classroom.objects
            .filter(Q(teacher=request.user) | Q(teachers=request.user))
            .distinct()
            .annotate(student_count=Count("memberships"))
        )

        return render(
            request,
            "dashboard_teacher.html",
            {
                "classrooms": classrooms,
            },
        )

    # ---------- STUDENT DASHBOARD ----------

    student_classrooms = (
        Classroom.objects
        .filter(memberships__student=request.user)
        .distinct()
    )


    assignments = (
        Assignment.objects
        .for_student(request.user)
        .select_related("classroom")
        .order_by("deadline")
    )

    submissions = Submission.objects.filter(
        student=request.user
    )

    submitted_ids = {s.assignment_id for s in submissions}
    graded_ids = {s.assignment_id for s in submissions if s.grade is not None}
    graded_map = {s.assignment_id: s.grade for s in submissions}
    feedback_map = {s.assignment_id: s.feedback for s in submissions}
    grader_map = {s.assignment_id: s.graded_by.username for s in submissions if s.graded_by}

    unread_alerts = Alert.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    read_alerts = Alert.objects.filter(user=request.user, is_read=True).order_by('-created_at')[:20]

    resources = Resource.objects.filter(
        classroom__in=student_classrooms
    ).select_related("classroom", "uploaded_by").order_by("-uploaded_at")

    return render(
        request,
        "dashboard_student.html",
        {
            "assignments": assignments,
            "submitted_ids": submitted_ids,
            "graded_ids": graded_ids,
            "graded_map": graded_map,
            "feedback_map": feedback_map,
            "grader_map": grader_map,
            "classrooms": student_classrooms,
            "unread_alerts": unread_alerts,
            "read_alerts": read_alerts,
            "now": timezone.now(),
            "resources": resources,
        },
    )


# =========================
# CLASSROOM PAGE
# =========================
@login_required
def classroom_detail(request, classroom_id):

    classroom = get_object_or_404(Classroom, id=classroom_id)

    # SECURITY: allow only teacher or enrolled students
    if not classroom.is_teacher(request.user):
        if not ClassroomMembership.objects.filter(
            classroom=classroom,
            student=request.user
        ).exists():
            return HttpResponseForbidden("You are not part of this classroom.")

    # assignments and announcements
    assignments = classroom.assignments.all()
    resources = Resource.objects.filter(classroom=classroom)

    stream_items = []

    for a in assignments:
        stream_items.append({
            "type": "assignment",
            "object": a,
            "time": a.created_at
        })

    for r in resources:
        stream_items.append({
            "type": "announcement",
            "object": r,
            "time": r.uploaded_at
        })

    # newest first
    stream_items.sort(key=lambda x: x["time"], reverse=True)

    # used by template
    is_teacher = classroom.is_teacher(request.user)
    is_owner = classroom.teacher == request.user

    return render(
        request,
        "classroom/classroom_detail.html",
        {
            "classroom": classroom,
            "stream_items": stream_items,
            "is_teacher": is_teacher,
            "is_owner": is_owner
        },
    )


# =========================
# POST ANNOUNCEMENT
# =========================
@login_required
def post_announcement(request, classroom_id):

    classroom = get_object_or_404(Classroom, id=classroom_id)

    # HARD SECURITY CHECK
    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Students cannot post announcements.")

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        uploaded_files = request.FILES.getlist("files")
        first_file = uploaded_files[0] if uploaded_files else None

        resource = Resource.objects.create(
            title=title,
            content=content,
            file=first_file,
            classroom=classroom,
            uploaded_by=request.user
        )

        # Save any additional files
        for f in uploaded_files[1:]:
            ResourceFile.objects.create(resource=resource, file=f)

    return redirect("classroom_detail", classroom_id=classroom.id)


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("login")


# =========================
# CREATE CLASSROOM
# =========================
@login_required
def create_classroom(request):

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student"},
    )
    if profile.role != "teacher":
        return HttpResponseForbidden("Only teachers can create classrooms.")

    created_classroom = None

    if request.method == "POST":

        name = request.POST.get("name")

        created_classroom = Classroom.objects.create(
            name=name,
            teacher=request.user,
        )

    return render(
        request,
        "classroom/create_classroom.html",
        {"created_classroom": created_classroom},
    )


# =========================
# JOIN CLASSROOM
# =========================
@login_required
def join_classroom(request):

    message = ""

    if request.method == "POST":

        code = request.POST.get("join_code")

        try:

            classroom = Classroom.objects.get(join_code=code)

            profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": "student"})
            if profile.role == "teacher":
                classroom.teachers.add(request.user)
                message = "Successfully joined as co-teacher!"
            else:
                ClassroomMembership.objects.get_or_create(
                    classroom=classroom,
                    student=request.user,
                )
                message = "Successfully joined!"

        except Classroom.DoesNotExist:

            message = "Invalid code"

    return render(
        request,
        "classroom/join_classroom.html",
        {"message": message},
    )


# =========================
# CLASSROOM STUDENTS
# =========================
@login_required
def classroom_students(request, classroom_id):

    classroom = get_object_or_404(
        Classroom,
        id=classroom_id,
    )

    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")

    members = (
        ClassroomMembership.objects
        .filter(classroom=classroom)
        .select_related("student")
    )

    return render(
        request,
        "classroom/classroom_students.html",
        {
            "classroom": classroom,
            "members": members,
        },
    )


# =========================
# EDIT CLASSROOM
# =========================
@login_required
def edit_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    # Check permission
    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("You do not have permission to edit this classroom.")

    error_message = None
    success_message = None

    if request.method == "POST":
        # Handle student removal
        if "remove_student" in request.POST:
            student_id = request.POST.get("student_id")
            membership = ClassroomMembership.objects.filter(classroom=classroom, student_id=student_id).first()
            if membership:
                username = membership.student.username
                membership.delete()
                messages.success(request, f"Student '{username}' has been removed.")
            return redirect("edit_classroom", classroom_id=classroom.id)
        
        # Handle classroom details update
        if "update_details" in request.POST:
            name = request.POST.get("name")
            if name:
                classroom.name = name
                classroom.save()
                messages.success(request, "Classroom details saved.")
            return redirect("edit_classroom", classroom_id=classroom.id)

        # Handle adding co-teacher
        if "add_coteacher" in request.POST:
            username = request.POST.get("coteacher_username")
            try:
                user_to_add = User.objects.get(username=username)
                profile, _ = Profile.objects.get_or_create(user=user_to_add, defaults={"role": "student"})
                
                if profile.role == "teacher":
                    if user_to_add == classroom.teacher or classroom.teachers.filter(id=user_to_add.id).exists():
                        error_message = f"User '{username}' is already a teacher in this classroom."
                    else:
                        classroom.teachers.add(user_to_add)
                        success_message = f"Successfully added '{username}' as a co-teacher."
                else:
                    error_message = f"User '{username}' is registered as a student. Only teachers can be added as co-teachers."
            except User.DoesNotExist:
                error_message = f"User '{username}' does not exist."
                
        # Handle removing co-teacher
        if "remove_coteacher" in request.POST:
            coteacher_id = request.POST.get("coteacher_id")
            classroom.teachers.remove(coteacher_id)
            messages.success(request, "Co-teacher removed.")
            return redirect("edit_classroom", classroom_id=classroom.id)

        # Handle adding student
        if "add_student" in request.POST:
            username = request.POST.get("student_username")
            try:
                user_to_add = User.objects.get(username=username)
                profile, _ = Profile.objects.get_or_create(user=user_to_add, defaults={"role": "student"})
                
                if profile.role == "student":
                    if ClassroomMembership.objects.filter(classroom=classroom, student=user_to_add).exists():
                        error_message = f"Student '{username}' is already in this classroom."
                    else:
                        ClassroomMembership.objects.create(classroom=classroom, student=user_to_add)
                        success_message = f"Successfully added student '{username}'."
                else:
                    error_message = f"User '{username}' is registered as a teacher and cannot be enrolled as a student."
            except User.DoesNotExist:
                error_message = f"User '{username}' does not exist."

    members = ClassroomMembership.objects.filter(classroom=classroom).select_related("student")
    
    enrolled_student_ids = members.values_list('student_id', flat=True)
    available_students = User.objects.filter(profile__role="student").exclude(id__in=enrolled_student_ids).order_by('username')

    co_teachers = classroom.teachers.all()

    return render(
        request,
        "classroom/edit_classroom.html",
        {
            "classroom": classroom,
            "members": members,
            "available_students": available_students,
            "co_teachers": co_teachers,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


# =========================
# ADD CO-TEACHER
# =========================
@login_required
def add_coteacher(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if classroom.teacher != request.user:
        return HttpResponseForbidden("Only the classroom owner can manage co-teachers.")

    error_message = None
    success_message = None

    if request.method == "POST":
        username = request.POST.get("coteacher_username")
        try:
            user_to_add = User.objects.get(username=username)
            profile, _ = Profile.objects.get_or_create(user=user_to_add, defaults={"role": "student"})
            
            if profile.role == "teacher":
                if user_to_add == classroom.teacher or classroom.teachers.filter(id=user_to_add.id).exists():
                    error_message = f"User '{username}' is already a teacher in this classroom."
                else:
                    classroom.teachers.add(user_to_add)
                    success_message = f"Successfully added '{username}' as a co-teacher."
            else:
                error_message = f"User '{username}' is a student. Only teachers can be co-teachers."
        except User.DoesNotExist:
            error_message = f"User '{username}' does not exist."

    co_teachers = classroom.teachers.all()
    
    current_teacher_ids = list(co_teachers.values_list('id', flat=True)) + [classroom.teacher.id]
    available_teachers = User.objects.filter(profile__role="teacher").exclude(id__in=current_teacher_ids).order_by('username')

    return render(
        request,
        "classroom/add_coteacher.html",
        {
            "classroom": classroom,
            "co_teachers": co_teachers,
            "available_teachers": available_teachers,
            "error_message": error_message,
            "success_message": success_message,
        }
    )


# =========================
# DELETE CLASSROOM
# =========================
@login_required
def delete_classroom(request, classroom_id):

    classroom = get_object_or_404(
        Classroom,
        id=classroom_id,
        teacher=request.user,
    )

    if request.method == "POST":
        classroom.delete()
        return redirect("dashboard")

    return redirect("classroom_detail", classroom_id=classroom.id)

@login_required
def mark_alert_read(request, alert_id):
    if request.method == "POST":
        alert = get_object_or_404(Alert, id=alert_id, user=request.user)
        alert.is_read = True
        alert.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))