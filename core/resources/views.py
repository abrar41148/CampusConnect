from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Resource
from main.models import Classroom, ClassroomMembership

@login_required
def upload_resource(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if not classroom.is_teacher(request.user):
        return HttpResponseForbidden("Only teachers can upload resources.")
    
    if request.method == "POST":
        title = request.POST.get("title")
        file = request.FILES.get("file")

        content = request.POST.get("content", "")

        Resource.objects.create(
            title=title,
            content=content,
            file=file,
            classroom=classroom,
            uploaded_by=request.user
        )

        return redirect("classroom_detail", classroom_id=classroom.id)

    return render(request, "resources/upload_resource.html", {"classroom": classroom})

@login_required
def resource_list(request):
    user_classrooms = Classroom.objects.filter(
        memberships__student=request.user
    ).distinct()
    resources = Resource.objects.filter(
        classroom__in=user_classrooms
    ).select_related('classroom', 'uploaded_by').order_by('-uploaded_at')
    return render(request, 'resources/resource_list.html', {
        'resources': resources
    })

@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if not resource.classroom.is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")
        
    if request.method == "POST":
        classroom_id = resource.classroom.id
        resource.delete()
        return redirect("classroom_detail", classroom_id=classroom_id)
        
    return redirect("classroom_detail", classroom_id=resource.classroom.id)
