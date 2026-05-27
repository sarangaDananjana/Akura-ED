from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminCourseViewSet, AdminSubCourseViewSet, AdminFlashcardViewSet,
    AdminMCQQuestionViewSet, AdminMCQOptionViewSet,
    SyncPushView, SyncPullView,
    ReadOnlyCourseViewSet, ReadOnlySubCourseViewSet, ReadOnlyFlashcardViewSet,
    ReadOnlyMCQQuestionViewSet
)

router = DefaultRouter()
# Register Admin endpoints
router.register(r'admin/courses', AdminCourseViewSet, basename='admin-courses')
router.register(r'admin/subcourses', AdminSubCourseViewSet,
                basename='admin-subcourses')
router.register(r'admin/flashcards', AdminFlashcardViewSet,
                basename='admin-flashcards')
router.register(r'admin/mcqs', AdminMCQQuestionViewSet, basename='admin-mcqs')
router.register(r'admin/mcq-options', AdminMCQOptionViewSet,
                basename='admin-mcq-options')

# Register Standard User endpoints
router.register(r'courses', ReadOnlyCourseViewSet, basename='courses')
router.register(r'subcourses', ReadOnlySubCourseViewSet, basename='subcourses')
router.register(r'flashcards', ReadOnlyFlashcardViewSet, basename='flashcards')
router.register(r'mcqs', ReadOnlyMCQQuestionViewSet, basename='mcqs')

urlpatterns = [
    path('sync/push/', SyncPushView.as_view(), name='sync-push'),
    path('sync/pull/', SyncPullView.as_view(), name='sync-pull'),
    path('', include(router.urls)),
]
