from django.contrib import admin
from .models import Course, SubCourse, Flashcard, MCQQuestion, MCQOption

admin.site.register(Course)
admin.site.register(SubCourse)
admin.site.register(Flashcard)
admin.site.register(MCQQuestion)
admin.site.register(MCQOption)
