from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from assignments.models import Assignment
from main.models import ClassroomMembership
from .models import Submission, SubmissionFile


@login_required
def submit_assignment(request, assignment_id):

    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Verify the student is enrolled in the classroom
    if not assignment.classroom.is_teacher(request.user):
        if not ClassroomMembership.objects.filter(
            classroom=assignment.classroom, student=request.user
        ).exists():
            return HttpResponseForbidden("You are not enrolled in this classroom.")

    is_past_deadline = timezone.now() > assignment.deadline

    if is_past_deadline and not assignment.allow_late_submissions:
        return HttpResponseForbidden("Late submissions are strictly prohibited for this assignment.")

    if request.method == "POST":
        uploaded_files = request.FILES.getlist("files")
        first_file = uploaded_files[0] if uploaded_files else None
        defaults = {"is_late": is_past_deadline}
        if first_file:
            defaults["file"] = first_file
            
        submission, created = Submission.objects.update_or_create(
            assignment=assignment,
            student=request.user,
            defaults=defaults
        )

        # Only touch files if the user actually uploaded new ones
        if uploaded_files:
            # If resubmitting, clear old extra files and save new ones
            if not created:
                submission.extra_files.all().delete()
            for f in uploaded_files[1:]:
                SubmissionFile.objects.create(submission=submission, file=f)

        return redirect("dashboard")

    return render(
        request,
        "submissions/submit_assignment.html",
        {
            "assignment": assignment,
            "is_past_deadline": is_past_deadline
        }
    )

@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Ensure only the teacher can view submissions
    if not assignment.classroom.is_teacher(request.user):
        return HttpResponseForbidden("You are not authorized to view these submissions.")
        
    submissions = Submission.objects.filter(assignment=assignment)
    
    if request.method == "POST":
        # Handle grading
        submission_id = request.POST.get("submission_id")
        grade = request.POST.get("grade")
        feedback = request.POST.get("feedback")
        
        if submission_id:
            sub = get_object_or_404(Submission, id=submission_id, assignment=assignment)
            grade_updated = False
            
            if grade is not None:
                # User intentionally typed an empty grade to clear it
                if str(grade).strip() == "":
                    if sub.grade is not None:
                        grade_updated = True
                        sub.grade = None
                        sub.graded_by = None
                else:
                    try:
                        parsed_grade = int(grade)
                    except (ValueError, TypeError):
                        return redirect("view_submissions", assignment_id=assignment.id)
                    if parsed_grade > assignment.max_grade:
                        parsed_grade = assignment.max_grade
                    if parsed_grade < 0:
                        parsed_grade = 0
                    
                    if sub.grade != parsed_grade:
                        grade_updated = True
                        sub.graded_by = request.user
                        
                    sub.grade = parsed_grade
                
            if feedback is not None:
                sub.feedback = feedback
                
            sub.save()
            
            if grade_updated and sub.grade is not None:
                from main.models import Alert
                Alert.objects.create(
                    user=sub.student,
                    message=f"Your assignment '{assignment.title}' has been graded by {sub.graded_by.username}: {sub.grade}/{assignment.max_grade}"
                )
            return redirect("view_submissions", assignment_id=assignment.id)

    return render(request, "submissions/view_submissions.html", {
        "assignment": assignment,
        "submissions": submissions
    })
