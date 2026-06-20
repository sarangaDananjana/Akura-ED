import os

file_path = r'c:\Users\Saranga\Desktop\Akura ED\learning\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption",
    "from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, CoursePurchase\nfrom django.db.models import Q"
)

content = content.replace(
    "DomainSerializer, CourseSerializer, SubCourseSerializer, FlashcardSerializer,\n    MCQQuestionSerializer, MCQOptionSerializer",
    "DomainSerializer, CourseSerializer, SubCourseSerializer, FlashcardSerializer,\n    MCQQuestionSerializer, MCQOptionSerializer, ShopCourseSerializer"
)

# 2. Update get_queryset for ReadOnly
subcourse_old = """class ReadOnlySubCourseViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for SubCourses.\"\"\"
    queryset = SubCourse.objects.filter(is_active=True).order_by('priority')
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset"""

subcourse_new = """class ReadOnlySubCourseViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for SubCourses.\"\"\"
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Allow if subcourse is free OR user has purchased the parent course
        queryset = SubCourse.objects.filter(is_active=True).filter(
            Q(is_free=True) | Q(course__purchases__user=user)
        ).distinct().order_by('priority')
        
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset"""
content = content.replace(subcourse_old, subcourse_new)

flashcard_old = """class ReadOnlyFlashcardViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for Flashcards.\"\"\"
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]"""

flashcard_new = """class ReadOnlyFlashcardViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for Flashcards.\"\"\"
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Flashcard.objects.filter(
            Q(subcourse__is_free=True) | Q(subcourse__course__purchases__user=user)
        ).distinct()"""
content = content.replace(flashcard_old, flashcard_new)

mcq_old = """class ReadOnlyMCQQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for MCQ Questions.\"\"\"
    queryset = MCQQuestion.objects.all()
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]"""

mcq_new = """class ReadOnlyMCQQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Read-only operations for MCQ Questions.\"\"\"
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MCQQuestion.objects.filter(
            Q(subcourse__is_free=True) | Q(subcourse__course__purchases__user=user)
        ).distinct()"""
content = content.replace(mcq_old, mcq_new)


# 3. Add Shop Views
shop_views = """

# --- Shop / E-Commerce Views ---

class ShopCourseViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"Lists all active courses in the shop, with pricing and purchase status.\"\"\"
    queryset = Course.objects.filter(is_active=True).order_by('priority')
    serializer_class = ShopCourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckoutView(APIView):
    \"\"\"
    Mock checkout endpoint.
    Expects {"course_id": <id>}
    Immediately grants the user access to the course.
    \"\"\"
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({"error": "course_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({"error": "Course not found or inactive."}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if already purchased
        if CoursePurchase.objects.filter(user=request.user, course=course).exists():
            return Response({"error": "You already own this course."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create purchase record (Mocking payment success)
        CoursePurchase.objects.create(
            user=request.user,
            course=course,
            amount_paid=course.price
        )
        
        return Response({"message": "Purchase successful! You now have access to the course."}, status=status.HTTP_201_CREATED)

"""

if "ShopCourseViewSet" not in content:
    content = content.replace("class AdminCSVUploadView", shop_views + "\nclass AdminCSVUploadView")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
