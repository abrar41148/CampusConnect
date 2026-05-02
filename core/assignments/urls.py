from django.urls import path
from .views import create_assignment, assignment_detail, edit_assignment, delete_assignment

urlpatterns = [
    path("classroom/<int:classroom_id>/create-assignment/", create_assignment, name="create_assignment"),
    path("assignment/<int:assignment_id>/", assignment_detail, name="assignment_detail"),
    path("assignment/<int:assignment_id>/edit/", edit_assignment, name="edit_assignment"),
    path("assignment/<int:assignment_id>/delete/", delete_assignment, name="delete_assignment"),
]
