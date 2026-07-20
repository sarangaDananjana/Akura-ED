from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDomainViewSet, AdminCourseViewSet, AdminSubCourseViewSet, AdminFlashcardViewSet,
    AdminMCQQuestionViewSet, AdminMCQOptionViewSet, AdminCSVUploadView,
    ReadOnlyDomainViewSet, ReadOnlyCourseViewSet, ReadOnlySubCourseViewSet, ReadOnlyFlashcardViewSet,
    ReadOnlyMCQQuestionViewSet,
    ShopCourseViewSet, EnrollmentView, MyEnrollmentsView,
    FlashcardSyncView, QuizStartView, QuizSubmitView, QuizScoresView,
    BannerViewSet, StudentQuestionViewSet, TeacherDashboardStatsView, TeacherQuestionViewSet, TeacherCourseViewSet
)

router = DefaultRouter()
# Register Admin endpoints
router.register(r'admin/domains', AdminDomainViewSet, basename='admin-domains')
router.register(r'admin/courses', AdminCourseViewSet, basename='admin-courses')
router.register(r'admin/subcourses', AdminSubCourseViewSet,
                basename='admin-subcourses')
router.register(r'admin/flashcards', AdminFlashcardViewSet,
                basename='admin-flashcards')
router.register(r'admin/mcqs', AdminMCQQuestionViewSet, basename='admin-mcqs')
router.register(r'admin/mcq-options', AdminMCQOptionViewSet,
                basename='admin-mcq-options')

# Register Standard User endpoints
router.register(r'domains', ReadOnlyDomainViewSet, basename='domains')
router.register(r'courses', ReadOnlyCourseViewSet, basename='courses')
router.register(r'subcourses', ReadOnlySubCourseViewSet, basename='subcourses')
router.register(r'flashcards', ReadOnlyFlashcardViewSet, basename='flashcards')
router.register(r'mcqs', ReadOnlyMCQQuestionViewSet, basename='mcqs')
router.register(r'banners', BannerViewSet, basename='banners')

# Register Shop endpoints
router.register(r'shop/courses', ShopCourseViewSet, basename='shop-courses')

# Teacher & Question endpoints
router.register(r'student-questions', StudentQuestionViewSet, basename='student-questions')
router.register(r'teacher-questions', TeacherQuestionViewSet, basename='teacher-questions')
router.register(r'teacher-courses', TeacherCourseViewSet, basename='teacher-courses')

urlpatterns = [
    path('api/flashcards/sync', FlashcardSyncView.as_view(), name='flashcard-sync'),
    path('api/quiz/start', QuizStartView.as_view(), name='quiz-start'),
    path('api/quiz/submit', QuizSubmitView.as_view(), name='quiz-submit'),
    path('api/quiz/scores', QuizScoresView.as_view(), name='quiz-scores'),
    path('admin/csv-upload/', AdminCSVUploadView.as_view(), name='admin-csv-upload'),
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('teacher-dashboard-stats/', TeacherDashboardStatsView.as_view(), name='teacher-dashboard-stats'),
    path('', include(router.urls)),
]
