from django.urls import path
from .views import resource_list, upload_resource, delete_resource

urlpatterns = [
    path('', resource_list, name='resource_list'),
    path("classroom/<int:classroom_id>/upload/", upload_resource, name="upload_resource"),
    path("resource/<int:resource_id>/delete/", delete_resource, name="delete_resource"),
]
