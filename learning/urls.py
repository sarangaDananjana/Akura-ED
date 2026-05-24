from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminSubCourseViewSet, AdminFlashcardViewSet,
    AdminMCQQuestionViewSet, AdminMCQOptionViewSet
)

router = DefaultRouter()
# Register Admin endpoints
router.register(r'admin/subcourses', AdminSubCourseViewSet,
                basename='admin-subcourses')
router.register(r'admin/flashcards', AdminFlashcardViewSet,
                basename='admin-flashcards')
router.register(r'admin/mcqs', AdminMCQQuestionViewSet, basename='admin-mcqs')
router.register(r'admin/mcq-options', AdminMCQOptionViewSet,
                basename='admin-mcq-options')

urlpatterns = [
    path('', include(router.urls)),
]
