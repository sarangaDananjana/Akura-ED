from django.contrib import admin
from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority')
    list_editable = ('priority',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'domain', 'is_active', 'priority')
    list_editable = ('priority',)
    list_filter = ('domain',)

@admin.register(SubCourse)
class SubCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_active', 'priority')
    list_editable = ('priority',)
    list_filter = ('course',)

admin.site.register(Flashcard)
admin.site.register(MCQQuestion)
admin.site.register(MCQOption)
