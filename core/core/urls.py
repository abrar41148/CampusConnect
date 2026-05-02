from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main.views import login_view, dashboard, logout_view
from main import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('alerts/mark-read/<int:alert_id>/', views.mark_alert_read, name='mark_alert_read'),

    path('logout/', logout_view, name='logout'),

    # classroom system
    path("classroom/create/", views.create_classroom, name="create_classroom"),
    path("classroom/join/", views.join_classroom, name="join_classroom"),

    path("classroom/<int:classroom_id>/", views.classroom_detail, name="classroom_detail"),
    path("classroom/<int:classroom_id>/edit/", views.edit_classroom, name="edit_classroom"),
    path("classroom/<int:classroom_id>/add_coteacher/", views.add_coteacher, name="add_coteacher"),
    path("classroom/<int:classroom_id>/students/", views.classroom_students, name="classroom_students"),
    path("classroom/<int:classroom_id>/delete/", views.delete_classroom, name="delete_classroom"),
    path("classroom/<int:classroom_id>/announcement/", views.post_announcement, name="post_announcement"),

    # Application Includes
    path('assignments/', include('assignments.urls')),
    path('submissions/', include('submissions.urls')),
    path('resources/', include('resources.urls')),
    path('attendance/', include('attendance.urls')),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )