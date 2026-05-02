from datetime import datetime
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import messages
from submissions.models import Submission

from assignments.models import Assignment, AssignmentFile
from main.models import Classroom, ClassroomMembership


@login_required
def create_assignment(request, classroom_id):

    classroom = get_object_or_404(
        Classroom,
        id=classroom_id,
    )

    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")

        deadline_date = request.POST.get("deadline_date")
        deadline_time = request.POST.get("deadline_time")

        try:
            date_obj = datetime.strptime(deadline_date, "%Y-%m-%d").date()
            time_obj = datetime.strptime(deadline_time, "%H:%M").time()
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid deadline date or time format.")

        deadline_naive = datetime.combine(date_obj, time_obj)
        deadline = timezone.make_aware(deadline_naive)

        max_grade = request.POST.get("max_grade", 100)
        
        allow_late = request.POST.get("allow_late_submissions") == "on"

        uploaded_files = request.FILES.getlist("files")
        first_file = uploaded_files[0] if uploaded_files else None

        assignment = Assignment.objects.create(
            title=title,
            description=description,
            deadline=deadline,
            max_grade=max_grade,
            allow_late_submissions=allow_late,
            classroom=classroom,
            created_by=request.user,
            file=first_file
        )

        # Save any additional files
        for f in uploaded_files[1:]:
            AssignmentFile.objects.create(assignment=assignment, file=f)

        return redirect("classroom_detail", classroom_id=classroom.id)

    return render(
        request,
        "assignments/create_assignment.html",
        {"classroom": classroom}
    )

@login_required
def assignment_detail(request, assignment_id):

    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Access check: only enrolled students or teachers can view
    if not assignment.classroom.is_teacher(request.user):
        if not ClassroomMembership.objects.filter(
            classroom=assignment.classroom, student=request.user
        ).exists():
            return HttpResponseForbidden("You are not part of this classroom.")

    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()

    return render(
        request,
        "assignments/assignment_detail.html",
        {
            "assignment": assignment,
            "submission": submission,
            "is_teacher": assignment.classroom.is_teacher(request.user),
            "is_past_deadline": timezone.now() > assignment.deadline
        }
    )

@login_required
def edit_assignment(request, assignment_id):

    assignment = get_object_or_404(Assignment, id=assignment_id)

    if not assignment.classroom.is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")

    if request.method == "POST":

        assignment.title = request.POST.get("title", assignment.title)
        assignment.description = request.POST.get("description", assignment.description)

        deadline_date = request.POST.get("deadline_date")
        deadline_time = request.POST.get("deadline_time")

        try:
            date_obj = datetime.strptime(deadline_date, "%Y-%m-%d").date()
            time_obj = datetime.strptime(deadline_time, "%H:%M").time()
            deadline_naive = datetime.combine(date_obj, time_obj)
            assignment.deadline = timezone.make_aware(deadline_naive)
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid deadline date or time format.")

        assignment.max_grade = request.POST.get("max_grade", assignment.max_grade)
        assignment.allow_late_submissions = request.POST.get("allow_late_submissions") == "on"

        # Replace primary file only if a new one was uploaded
        uploaded_files = request.FILES.getlist("files")
        if uploaded_files:
            assignment.file = uploaded_files[0]
            # Add any additional new files
            for f in uploaded_files[1:]:
                AssignmentFile.objects.create(assignment=assignment, file=f)

        # Remove files the teacher unchecked
        remove_ids = request.POST.getlist("remove_files")
        if remove_ids:
            AssignmentFile.objects.filter(id__in=remove_ids, assignment=assignment).delete()

        assignment.save()
        messages.success(request, "Assignment updated successfully.")
        return redirect("assignment_detail", assignment_id=assignment.id)

    return render(
        request,
        "assignments/edit_assignment.html",
        {"assignment": assignment, "classroom": assignment.classroom}
    )

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.classroom.is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")
    
    if request.method == "POST":
        classroom_id = assignment.classroom.id
        assignment.delete()
        return redirect("classroom_detail", classroom_id=classroom_id)
        
    return redirect("classroom_detail", classroom_id=assignment.classroom.id)