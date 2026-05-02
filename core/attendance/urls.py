from django.urls import path
from .views import record_attendance, attendance_history, attendance_session_detail, student_attendance, global_student_attendance

urlpatterns = [
    path("classroom/<int:classroom_id>/record/", record_attendance, name="record_attendance"),
    path("classroom/<int:classroom_id>/history/", attendance_history, name="attendance_history"),
    path("session/<int:session_id>/", attendance_session_detail, name="attendance_session_detail"),
    path("classroom/<int:classroom_id>/my-attendance/", student_attendance, name="student_attendance"),
    path("my-attendance/", global_student_attendance, name="global_student_attendance"),
]
