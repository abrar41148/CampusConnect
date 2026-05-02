from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Classroom, ClassroomMembership

class ClassroomAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            kwargs["queryset"] = User.objects.filter(profile__role="teacher")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "students":
            kwargs["queryset"] = User.objects.filter(profile__role="student")
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Profile)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(ClassroomMembership)