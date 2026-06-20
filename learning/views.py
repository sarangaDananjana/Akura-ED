import os
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

import csv
import io
from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, Enrollment
from django.db.models import Q
from .serializers import (
    DomainSerializer, CourseSerializer, SubCourseSerializer, FlashcardSerializer,
    MCQQuestionSerializer, MCQOptionSerializer, ShopCourseSerializer
)

# Initialize MongoClient globally for connection pooling across requests
MONGO_URI = os.getenv('MONGO_URI')
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None

# Select the specific MongoDB database to use
mongo_db = mongo_client['edtech_progress_db'] if mongo_client else None


class SyncPushView(APIView):
    """
    API endpoint for the Flutter mobile app to push 'Delta' queue progress 
    (MCQs and Flashcards) to MongoDB Atlas.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not mongo_db:
            return Response(
                {"error": "MongoDB is not configured on the server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user_id = request.user.id
        data = request.data

        mcqs_data = data.get('mcqs', [])
        flashcards_data = data.get('flashcards', [])

        mcq_operations = []
        flashcard_operations = []

        # 1. Prepare MCQ updates
        for mcq in mcqs_data:
            subcourse_id = mcq.get('subcourse_id')
            answers = mcq.get('answers', {})
            
            if not subcourse_id or not answers:
                continue

            set_fields = {}
            for q_id_str, answer in answers.items():
                set_fields[f'answers.{q_id_str}'] = answer

            mcq_operations.append(
                UpdateOne(
                    {'user_id': user_id, 'subcourse_id': subcourse_id},
                    {'$set': set_fields},
                    upsert=True
                )
            )

        # 2. Prepare Flashcard updates
        for fc in flashcards_data:
            card_id = fc.get('card_id')
            if not card_id:
                continue

            update_doc = {
                '$set': {
                    'status': fc.get('status'),
                    'next_review': fc.get('next_review'),
                }
            }

            # Optional history append
            timestamp = fc.get('timestamp')
            if timestamp:
                interaction = {
                    'status': fc.get('status'),
                    'timestamp': timestamp
                }
                update_doc['$push'] = {
                    'history': {
                        '$each': [interaction],
                        '$slice': -3  # Keep only the last 3 interactions
                    }
                }

            flashcard_operations.append(
                UpdateOne(
                    {'user_id': user_id, 'card_id': card_id},
                    update_doc,
                    upsert=True
                )
            )

        # 3. Execute Bulk Writes
        try:
            if mcq_operations:
                mongo_db['mcq_progress'].bulk_write(mcq_operations, ordered=False)

            if flashcard_operations:
                mongo_db['flashcard_progress'].bulk_write(flashcard_operations, ordered=False)

            return Response({"message": "Progress synced successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncPullView(APIView):
    """
    API endpoint for the Flutter mobile app to pull the 'Complete' progress record 
    (MCQs and Flashcards) from MongoDB Atlas.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not mongo_db:
            return Response(
                {"error": "MongoDB is not configured on the server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user_id = request.user.id

        try:
            # Query the user's progress records, projecting out MongoDB _id and user_id
            mcq_cursor = mongo_db['mcq_progress'].find(
                {"user_id": user_id},
                {"_id": 0, "user_id": 0}
            )
            flashcard_cursor = mongo_db['flashcard_progress'].find(
                {"user_id": user_id},
                {"_id": 0, "user_id": 0}
            )

            # Convert cursors to lists
            mcqs_list = list(mcq_cursor)
            flashcards_list = list(flashcard_cursor)

            return Response({
                "mcqs": mcqs_list,
                "flashcards": flashcards_list
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Custom Admin Panel Views ---
# All views here require the user to have an Admin account (is_staff=True)

class BulkDeleteMixin:
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(id__in=ids)
        deleted_count, _ = queryset.delete()
        return Response({"message": f"Successfully deleted {deleted_count} items."}, status=status.HTTP_200_OK)

class AdminDomainViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for Domains in Custom Admin Panel."""
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminCourseViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for Courses in Custom Admin Panel."""
    queryset = Course.objects.all().order_by('priority')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        domain_id = self.request.query_params.get('domain_id')
        if domain_id:
            queryset = queryset.filter(domain_id=domain_id)
        return queryset


class AdminSubCourseViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for SubCourses in Custom Admin Panel."""
    queryset = SubCourse.objects.all().order_by('priority')
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class AdminFlashcardViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for Flashcards. Allows uploading text, image, voice."""
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminMCQQuestionViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for MCQ Questions."""
    queryset = MCQQuestion.objects.all()
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminMCQOptionViewSet(viewsets.ModelViewSet):
    """CRUD operations for MCQ Options.
    Admin can create, update, or delete answer rows here."""
    queryset = MCQOption.objects.all()
    serializer_class = MCQOptionSerializer
    permission_classes = [permissions.IsAdminUser]


# --- Standard User (Read-Only) Views ---
# These endpoints allow authenticated users to fetch the curriculum data.

class ReadOnlyDomainViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for Domains."""
    queryset = Domain.objects.filter(is_active=True).order_by('priority')
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReadOnlyCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for Courses."""
    queryset = Course.objects.filter(is_active=True).order_by('priority')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        domain_id = self.request.query_params.get('domain_id')
        if domain_id:
            queryset = queryset.filter(domain_id=domain_id)
        return queryset


class ReadOnlySubCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for SubCourses."""
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Allow if subcourse is free OR user has enrolled in parent course OR user enrolled directly
        queryset = SubCourse.objects.filter(is_active=True).filter(
            Q(is_free=True) | Q(course__enrollments__user=user) | Q(enrollments__user=user)
        ).distinct().order_by('priority')
        
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class ReadOnlyFlashcardViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for Flashcards."""
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Flashcard.objects.filter(
            Q(subcourse__is_free=True) | Q(subcourse__enrollments__user=user) | Q(subcourse__course__enrollments__user=user)
        ).distinct()


class ReadOnlyMCQQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for MCQ Questions."""
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MCQQuestion.objects.filter(
            Q(subcourse__is_free=True) | Q(subcourse__enrollments__user=user) | Q(subcourse__course__enrollments__user=user)
        ).distinct()




# --- Shop / E-Commerce Views ---

class ShopCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all active courses in the shop, with pricing and purchase status."""
    queryset = Course.objects.filter(is_active=True).order_by('priority')
    serializer_class = ShopCourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class EnrollmentView(APIView):
    """
    Endpoint to enroll in a free sub-course or purchase a parent course.
    Expects {"course_id": <id>} OR {"subcourse_id": <id>}
    """
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
    """
    Returns a list of all courses and sub-courses the user is enrolled in.
    """
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



class AdminCSVUploadView(APIView):
    """
    API endpoint for Admin to upload a CSV file and bulk create
    Flashcards or MCQs for a specific SubCourse.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        upload_type = request.data.get('type')
        subcourse_id = request.data.get('subcourse_id')
        start_row = int(request.data.get('start_row', 1))
        end_row = int(request.data.get('end_row', -1))
        file = request.FILES.get('file')

        if not all([upload_type, subcourse_id, file]):
            return Response({"error": "Missing required fields (type, subcourse_id, file)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subcourse = SubCourse.objects.get(id=subcourse_id)
        except SubCourse.DoesNotExist:
            return Response({"error": "SubCourse not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Read and decode CSV (utf-8-sig removes BOM if present)
            try:
                decoded_file = file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                file.seek(0)
                decoded_file = file.read().decode('latin-1')

            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            rows = list(reader)

            # Find the header row
            header_idx = -1
            for idx, row in enumerate(rows):
                if row:
                    clean_row = [str(cell).strip().lower().replace(' ', '').replace('_', '') for cell in row]
                    if 'questionid' in clean_row or 'questiontext' in clean_row:
                        header_idx = idx
                        break
            
            if header_idx == -1:
                return Response({"error": "Could not find header row containing Question Text or Question ID."}, status=status.HTTP_400_BAD_REQUEST)

            headers = [h.strip() for h in rows[header_idx]]
            data_rows = rows[header_idx + 1:]

            if end_row == -1 or end_row > len(data_rows):
                end_row = len(data_rows)
            
            if start_row < 1:
                start_row = 1

            # Slicing the data rows (start_row is 1-based index)
            target_rows = data_rows[start_row - 1 : end_row]

            created_count = 0

            def get_col_val(r_dict, possible_names):
                # Try exact match first
                for n in possible_names:
                    if n in r_dict:
                        return r_dict[n].strip()
                # Try fuzzy match
                for k, v in r_dict.items():
                    clean_k = k.lower().replace(' ', '').replace('_', '')
                    for n in possible_names:
                        if clean_k == n.lower().replace(' ', '').replace('_', ''):
                            return v.strip()
                return ''

            if upload_type == 'flashcard':
                for row_data in target_rows:
                    row_dict = dict(zip(headers, row_data))
                    q_text = get_col_val(row_dict, ['Question_Text', 'Question Text'])
                    ans_desc = get_col_val(row_dict, ['Answer_Text', 'Answer Text', 'Correct_Description', 'Correct Description'])
                    ans_text = get_col_val(row_dict, ['Answer'])
                    
                    if not ans_text:
                        # Find the option with 'correct' status
                        for i in range(1, 6):
                            opt_status = get_col_val(row_dict, [f'Status_{i}', f'Status {i}']).lower()
                            if opt_status == 'correct':
                                ans_text = get_col_val(row_dict, [f'Option_{i}', f'Option {i}'])
                                break

                    if q_text and ans_text:
                        Flashcard.objects.create(
                            subcourse=subcourse,
                            question_text=q_text,
                            answer=ans_text,
                            answer_text=ans_desc
                        )
                        created_count += 1
                        
            elif upload_type == 'mcq':
                for row_data in target_rows:
                    row_dict = dict(zip(headers, row_data))
                    q_text = get_col_val(row_dict, ['Question_Text', 'Question Text'])
                    if not q_text:
                        continue
                    
                    question = MCQQuestion.objects.create(
                        subcourse=subcourse,
                        text=q_text
                    )
                    
                    for i in range(1, 6):
                        opt_text = get_col_val(row_dict, [f'Option_{i}', f'Option {i}'])
                        opt_status = get_col_val(row_dict, [f'Status_{i}', f'Status {i}']).lower()
                        
                        if opt_text:
                            is_correct = (opt_status == 'correct')
                            MCQOption.objects.create(
                                question=question,
                                text=opt_text,
                                is_correct=is_correct
                            )
                    created_count += 1
            else:
                return Response({"error": "Invalid upload type. Must be 'flashcard' or 'mcq'."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": f"Successfully created {created_count} {upload_type}(s)."
            }, status=status.HTTP_201_CREATED)

        except UnicodeDecodeError:
             # Try utf-8-sig or latin-1 if utf-8 fails
             return Response({"error": "File encoding not supported. Please save as UTF-8 CSV."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
