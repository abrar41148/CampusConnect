from django.urls import path
from .views import view_submissions, submit_assignment

urlpatterns = [
    path("assignment/<int:assignment_id>/submit/", submit_assignment, name="submit_assignment"),
    path("assignment/<int:assignment_id>/view/", view_submissions, name="view_submissions"),
]
