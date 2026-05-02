from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.http import HttpResponseForbidden

from .models import AttendanceSession, Attendance
from main.models import Classroom, ClassroomMembership, Alert

@login_required
def record_attendance(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    
    # Ensure only the teacher can record attendance
    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Only the teacher can record attendance.")

    students = ClassroomMembership.objects.filter(classroom=classroom).select_related('student')

    if request.method == "POST":
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # 1. Create the session group
        session = AttendanceSession.objects.create(
            classroom=classroom,
            date=date,
            start_time=start_time,
            end_time=end_time,
            recorded_by=request.user
        )

        # 2. Extract statuses and save Attendance records
        attendances = []
        absent_alerts = []
        
        for membership in students:
            student_id = str(membership.student.id)
            # The form will send a radio/checkbox value like "status_12=Present"
            status = request.POST.get(f"status_{student_id}", "Absent")
            attendances.append(
                Attendance(session=session, student=membership.student, status=status)
            )
            
            if status == "Absent":
                absent_alerts.append(
                    Alert(
                        user=membership.student,
                        message=f"You were marked Absent by {request.user.username} for {classroom.name} on {date} during the {start_time} - {end_time} session."
                    )
                )
                
        Attendance.objects.bulk_create(attendances)
        if absent_alerts:
            Alert.objects.bulk_create(absent_alerts)
            
        return redirect('classroom_detail', classroom_id=classroom.id)

    # Defaults for GET request
    ist = ZoneInfo('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    current_date = now.strftime('%Y-%m-%d')
    # Round down to nearest hour, e.g. 10:30 -> 10:00
    current_hour_time = now.replace(minute=0, second=0).strftime('%H:%M')
    
    return render(request, "attendance/record_attendance.html", {
        "classroom": classroom,
        "students": students,
        "default_date": current_date,
        "default_start_time": current_hour_time
    })

@login_required
def attendance_history(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Only the teacher can view attendance history.")
        
    sessions = AttendanceSession.objects.filter(classroom=classroom).order_by('-date', '-start_time')
    return render(request, "attendance/attendance_history.html", {
        "classroom": classroom,
        "sessions": sessions
    })

@login_required
def attendance_session_detail(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    if not session.classroom.is_teacher(request.user):
        return HttpResponseForbidden("Only the teacher can view this session.")
        
    # Get all attendance records for this session, with student details
    attendances = Attendance.objects.filter(session=session).select_related('student').order_by('student__username')
    
    # Calculate summary stats
    total_present = attendances.filter(status='Present').count()
    total_absent = attendances.filter(status='Absent').count()
    total_students = attendances.count()
    
    edit_mode = False
    password_error = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "unlock_edit":
            # Password verification step
            from django.contrib.auth import authenticate
            password = request.POST.get("password")
            user = authenticate(request, username=request.user.username, password=password)
            if user is not None:
                edit_mode = True
            else:
                password_error = "Incorrect password. Please try again."
                
        elif action == "save_attendance":
            # Save changes
            session.recorded_by = request.user
            session.save()

            for attendance in attendances:
                student_id = str(attendance.student.id)
                new_status = request.POST.get(f"status_{student_id}")
                if new_status and new_status in ["Present", "Absent"]:
                    if attendance.status != new_status:
                        attendance.status = new_status
                        attendance.save()
                        
                        if new_status == "Absent":
                            Alert.objects.create(
                                user=attendance.student,
                                message=f"Your attendance for {session.classroom.name} on {session.date} ({session.start_time} - {session.end_time}) was changed to Absent by {request.user.username}."
                            )
            return redirect('attendance_session_detail', session_id=session.id)

    return render(request, "attendance/attendance_session_detail.html", {
        "session": session,
        "attendances": attendances,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_students": total_students,
        "edit_mode": edit_mode,
        "password_error": password_error,
    })

@login_required
def student_attendance(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    
    # Ensure the user is naturally a student of this classroom
    is_enrolled = ClassroomMembership.objects.filter(classroom=classroom, student=request.user).exists()
    if not is_enrolled and not classroom.is_teacher(request.user):
        return HttpResponseForbidden("You do not have permission to view this attendance record.")
        
    # Get all attendance records for this student in this classroom
    attendances = Attendance.objects.filter(
        session__classroom=classroom, 
        student=request.user
    ).select_related('session').order_by('-session__date', '-session__start_time')
    
    # Calculate summary stats
    total_present = attendances.filter(status='Present').count()
    total_absent = attendances.filter(status='Absent').count()
    total_sessions = attendances.count()
    
    attendance_percentage = 0
    if total_sessions > 0:
        attendance_percentage = round((total_present / total_sessions) * 100)
    
    return render(request, "attendance/student_attendance.html", {
        "classroom": classroom,
        "attendances": attendances,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_sessions": total_sessions,
        "attendance_percentage": attendance_percentage
    })

@login_required
def global_student_attendance(request):
    # Fetch all classrooms the user is in
    memberships = ClassroomMembership.objects.filter(student=request.user).select_related('classroom')
    
    attendance_summary = []
    
    for membership in memberships:
        classroom = membership.classroom
        # Calculate stats explicitly for this student in this classroom
        attendances = Attendance.objects.filter(session__classroom=classroom, student=request.user)
        total_sessions = attendances.count()
        total_present = attendances.filter(status='Present').count()
        total_absent = total_sessions - total_present
        percentage = round((total_present / total_sessions) * 100) if total_sessions > 0 else 0
        
        attendance_summary.append({
            'classroom': classroom,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_sessions': total_sessions,
            'percentage': percentage
        })
        
    return render(request, "attendance/global_student_attendance.html", {"attendance_summary": attendance_summary})
