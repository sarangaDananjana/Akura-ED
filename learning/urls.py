from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDomainViewSet, AdminCourseViewSet, AdminSubCourseViewSet, AdminFlashcardViewSet,
    AdminMCQQuestionViewSet, AdminMCQOptionViewSet, AdminCSVUploadView,
    SyncPushView, SyncPullView,
    ReadOnlyDomainViewSet, ReadOnlyCourseViewSet, ReadOnlySubCourseViewSet, ReadOnlyFlashcardViewSet,
    ReadOnlyMCQQuestionViewSet,
    ShopCourseViewSet, EnrollmentView, MyEnrollmentsView
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

# Register Shop endpoints
router.register(r'shop/courses', ShopCourseViewSet, basename='shop-courses')

urlpatterns = [
    path('sync/push/', SyncPushView.as_view(), name='sync-push'),
    path('sync/pull/', SyncPullView.as_view(), name='sync-pull'),
    path('admin/csv-upload/', AdminCSVUploadView.as_view(), name='admin-csv-upload'),
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('', include(router.urls)),
]
