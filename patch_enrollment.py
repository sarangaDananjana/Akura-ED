import os

dir_path = r'c:\Users\Saranga\Desktop\Akura ED\learning'

# 1. Update serializers.py
s_path = os.path.join(dir_path, 'serializers.py')
with open(s_path, 'r', encoding='utf-8') as f:
    s_cont = f.read()

s_cont = s_cont.replace(
    "from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption",
    "from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, Enrollment"
)

s_cont = s_cont.replace(
    "return obj.purchases.filter(user=user).exists()",
    "return obj.enrollments.filter(user=user).exists()"
)

enrollment_serializer = """

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
"""

if "EnrollmentSerializer" not in s_cont:
    s_cont += enrollment_serializer

with open(s_path, 'w', encoding='utf-8') as f:
    f.write(s_cont)


# 2. Update views.py
v_path = os.path.join(dir_path, 'views.py')
with open(v_path, 'r', encoding='utf-8') as f:
    v_cont = f.read()

v_cont = v_cont.replace("CoursePurchase", "Enrollment")

v_cont = v_cont.replace(
    "Q(course__purchases__user=user)",
    "Q(course__enrollments__user=user)"
)

v_cont = v_cont.replace(
    "Q(subcourse__course__purchases__user=user)",
    "Q(subcourse__enrollments__user=user) | Q(subcourse__course__enrollments__user=user)"
)

checkout_old = """class CheckoutView(APIView):
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
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({"error": "You already own this course."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create purchase record (Mocking payment success)
        Enrollment.objects.create(
            user=request.user,
            course=course,
            amount_paid=course.price
        )
        
        return Response({"message": "Purchase successful! You now have access to the course."}, status=status.HTTP_201_CREATED)"""

enroll_new = """class EnrollmentView(APIView):
    \"\"\"
    Endpoint to enroll in a free sub-course or purchase a parent course.
    Expects {"course_id": <id>} OR {"subcourse_id": <id>}
    \"\"\"
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        subcourse_id = request.data.get('subcourse_id')
        
        if not course_id and not subcourse_id:
            return Response({"error": "course_id or subcourse_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        if course_id:
            try:
                course = Course.objects.get(id=course_id, is_active=True)
            except Course.DoesNotExist:
                return Response({"error": "Course not found or inactive."}, status=status.HTTP_404_NOT_FOUND)
                
            if Enrollment.objects.filter(user=request.user, course=course).exists():
                return Response({"error": "You are already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)
                
            Enrollment.objects.create(
                user=request.user,
                course=course,
                amount_paid=course.price
            )
            return Response({"message": "Successfully enrolled in course!"}, status=status.HTTP_201_CREATED)
            
        if subcourse_id:
            try:
                subcourse = SubCourse.objects.get(id=subcourse_id, is_active=True)
            except SubCourse.DoesNotExist:
                return Response({"error": "SubCourse not found or inactive."}, status=status.HTTP_404_NOT_FOUND)
                
            if not subcourse.is_free:
                return Response({"error": "This sub-course is not free. You must purchase the parent course."}, status=status.HTTP_403_FORBIDDEN)
                
            if Enrollment.objects.filter(user=request.user, subcourse=subcourse).exists():
                return Response({"error": "You are already enrolled in this free sub-course."}, status=status.HTTP_400_BAD_REQUEST)
                
            Enrollment.objects.create(
                user=request.user,
                subcourse=subcourse,
                amount_paid=0.00
            )
            return Response({"message": "Successfully enrolled in free sub-course!"}, status=status.HTTP_201_CREATED)

class MyEnrollmentsView(APIView):
    \"\"\"
    Returns a list of all courses and sub-courses the user is enrolled in.
    \"\"\"
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        enrollments = Enrollment.objects.filter(user=request.user)
        
        courses = []
        subcourses = []
        
        for e in enrollments:
            if e.course:
                # We could serialize properly, but returning dicts is fine for this endpoint
                courses.append({
                    "id": e.course.id,
                    "title": e.course.title,
                    "enrolled_at": e.enrolled_at
                })
            if e.subcourse:
                subcourses.append({
                    "id": e.subcourse.id,
                    "title": e.subcourse.title,
                    "enrolled_at": e.enrolled_at
                })
                
        return Response({
            "courses": courses,
            "subcourses": subcourses
        }, status=status.HTTP_200_OK)
"""
v_cont = v_cont.replace(checkout_old, enroll_new)

# Update read-only SubCourse view to allow if enrolled in subcourse
subcourse_old_query = """        # Allow if subcourse is free OR user has purchased the parent course
        queryset = SubCourse.objects.filter(is_active=True).filter(
            Q(is_free=True) | Q(course__enrollments__user=user)
        ).distinct().order_by('priority')"""
subcourse_new_query = """        # Allow if subcourse is free OR user has enrolled in parent course OR user enrolled directly
        queryset = SubCourse.objects.filter(is_active=True).filter(
            Q(is_free=True) | Q(course__enrollments__user=user) | Q(enrollments__user=user)
        ).distinct().order_by('priority')"""
v_cont = v_cont.replace(subcourse_old_query, subcourse_new_query)

with open(v_path, 'w', encoding='utf-8') as f:
    f.write(v_cont)


# 3. Update urls.py
u_path = os.path.join(dir_path, 'urls.py')
with open(u_path, 'r', encoding='utf-8') as f:
    u_cont = f.read()

u_cont = u_cont.replace("CheckoutView", "EnrollmentView, MyEnrollmentsView")
u_cont = u_cont.replace("path('shop/checkout/', CheckoutView.as_view(), name='shop-checkout'),", 
                        "path('learning/enroll/', EnrollmentView.as_view(), name='enroll'),\n    path('learning/my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),")

with open(u_path, 'w', encoding='utf-8') as f:
    f.write(u_cont)
