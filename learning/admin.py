from django.contrib import admin
from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, Enrollment, Banner, Question

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority')
    list_editable = ('priority', 'is_active')
    search_fields = ('title', 'description')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'domain', 'price', 'is_active', 'priority')
    list_editable = ('priority', 'is_active', 'price')
    list_filter = ('domain', 'is_active')
    search_fields = ('title', 'description')
    filter_horizontal = ('teachers',)

@admin.register(SubCourse)
class SubCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_free', 'is_active', 'priority')
    list_editable = ('priority', 'is_free', 'is_active')
    list_filter = ('course', 'is_free', 'is_active')
    search_fields = ('title', 'description')

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_question_preview', 'subcourse', 'order')
    list_editable = ('order',)
    list_filter = ('subcourse',)
    search_fields = ('question_text', 'answer_text')

    def get_question_preview(self, obj):
        return obj.question_text[:50]
    get_question_preview.short_description = 'Question'

@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_text_preview', 'subcourse')
    list_filter = ('subcourse',)
    search_fields = ('text',)

    def get_text_preview(self, obj):
        return obj.text[:50]
    get_text_preview.short_description = 'Question Text'

@admin.register(MCQOption)
class MCQOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_editable = ('is_correct',)
    list_filter = ('is_correct', 'question__subcourse')
    search_fields = ('text', 'question__text')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subcourse', 'amount_paid', 'enrolled_at')
    list_filter = ('course', 'subcourse', 'enrolled_at')
    search_fields = ('user__username', 'user__email', 'course__title', 'subcourse__title')
    readonly_fields = ('enrolled_at',)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'is_answered', 'created_at')
    list_filter = ('is_answered', 'course', 'created_at')
    search_fields = ('student__username', 'student__email', 'course__title', 'text')
    readonly_fields = ('created_at',)

