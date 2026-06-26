import os
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from pymongo import MongoClient, UpdateOne
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

import csv
import io
from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, Enrollment, Banner
from django.db.models import Q
from .serializers import (
    DomainSerializer, CourseSerializer, SubCourseSerializer, FlashcardSerializer,
    MCQQuestionSerializer, MCQOptionSerializer, ShopCourseSerializer, BannerSerializer
)

# Initialize MongoClient globally for connection pooling across requests
MONGO_URI = os.getenv('MONGO_URI')
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None

# Select the specific MongoDB database to use
mongo_db = mongo_client['edtech_progress_db'] if mongo_client else None


class FlashcardSyncView(APIView):
    """
    API endpoint to batch sync flashcard reviews (e.g., after 20 swipes).
    Executes a bulk write to 'FlashcardProgress' collection.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not mongo_db:
            return Response({"error": "MongoDB not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_id = str(request.user.id)
        # Fetch the progress for this user
        progress_cursor = mongo_db['FlashcardProgress'].find({'userId': user_id})
        
        # Format it into a clean list
        progress_list = []
        for doc in progress_cursor:
            progress_list.append({
                'flashcardId': doc.get('flashcardId'),
                'status': doc.get('status')
            })
            
        return Response(progress_list, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not mongo_db:
            return Response({"error": "MongoDB not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_id = str(request.user.id)
        reviews = request.data.get('reviews', [])

        if not reviews:
            return Response({"error": "No reviews provided."}, status=status.HTTP_400_BAD_REQUEST)

        operations = []
        for review in reviews:
            flashcard_id = str(review.get('flashcardId'))
            if not flashcard_id:
                continue

            # In a real app, you might use spaced repetition logic to determine lastReviewedAt and reviewCount.
            update_doc = {
                '$set': {
                    'status': review.get('status'),
                    'lastReviewedAt': timezone.now()
                },
                '$inc': {
                    'reviewCount': 1
                }
            }

            operations.append(
                UpdateOne(
                    {'userId': user_id, 'flashcardId': flashcard_id},
                    update_doc,
                    upsert=True
                )
            )

        if operations:
            try:
                mongo_db['FlashcardProgress'].bulk_write(operations, ordered=False)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Flashcard progress synced"}, status=status.HTTP_200_OK)


class QuizStartView(APIView):
    """
    Starts a quiz attempt.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not mongo_db:
            return Response({"error": "MongoDB not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_id = str(request.user.id)
        quiz_id = str(request.data.get('quizId'))

        if not quiz_id:
            return Response({"error": "quizId is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing completed sessions
        existing_sessions = mongo_db['QuizSessions'].find(
            {'userId': user_id, 'quizId': quiz_id, 'status': 'completed'}
        )
        existing_count = len(list(existing_sessions))

        session_id = f"session_{uuid.uuid4().hex}"
        now = timezone.now()
        expires_at = now + timedelta(minutes=15)

        if existing_count == 0:
            # First attempt (Official)
            doc = {
                '_id': session_id,
                'userId': user_id,
                'quizId': quiz_id,
                'attemptNumber': 1,
                'status': 'in_progress',
                'startTime': now,
                'expiresAt': expires_at,
                'totalScore': 0,
                'answers': []
            }
            mongo_db['QuizSessions'].insert_one(doc)
            return Response({
                "sessionId": session_id,
                "isOfficial": True,
                "expiresAt": expires_at
            }, status=status.HTTP_200_OK)
        else:
            # Practice mode
            attempt_number = existing_count + 1
            doc = {
                '_id': session_id,
                'userId': user_id,
                'quizId': quiz_id,
                'attemptNumber': attempt_number,
                'status': 'in_progress',
                'startTime': now,
                'expiresAt': expires_at,
                'totalScore': 0,
                'answers': []
            }
            mongo_db['QuizSessions'].insert_one(doc)
            return Response({
                "sessionId": session_id,
                "isOfficial": False,
                "expiresAt": expires_at
            }, status=status.HTTP_200_OK)


class QuizSubmitView(APIView):
    """
    Submits a quiz attempt.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not mongo_db:
            return Response({"error": "MongoDB not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_id = str(request.user.id)
        session_id = request.data.get('sessionId')
        answers = request.data.get('answers', [])

        if not session_id:
            return Response({"error": "sessionId is required."}, status=status.HTTP_400_BAD_REQUEST)

        session = mongo_db['QuizSessions'].find_one({'_id': session_id, 'userId': user_id})
        if not session:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session['status'] != 'in_progress':
            return Response({"error": "Session is already completed or abandoned."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        is_official = session['attemptNumber'] == 1

        if is_official and session['expiresAt'] and now > session['expiresAt']:
            # Mark as abandoned/expired
            mongo_db['QuizSessions'].update_one(
                {'_id': session_id},
                {'$set': {'status': 'abandoned', 'totalScore': 0, 'answers': []}}
            )
            return Response({"error": "Time limit exceeded. Session abandoned."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate score locally for security (in real scenario, cross check with DB)
        # Assuming the app passes `isCorrect` for simplicity of this architectural update:
        total_score = sum(1 for ans in answers if ans.get('isCorrect'))
        
        # Here you could update the leaderboard profile if it's the first attempt
        if is_official:
            pass # TODO: Leaderboard update logic goes here

        mongo_db['QuizSessions'].update_one(
            {'_id': session_id},
            {
                '$set': {
                    'status': 'completed',
                    'totalScore': total_score,
                    'answers': answers
                }
            }
        )

        return Response({
            "message": "Quiz submitted successfully",
            "totalScore": total_score,
            "isOfficial": is_official
        }, status=status.HTTP_200_OK)


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

from rest_framework.decorators import action


class AdminFlashcardViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for Flashcards. Allows uploading text, image, voice."""
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        subcourse_id = self.request.query_params.get('subcourse_id')
        if subcourse_id:
            queryset = queryset.filter(subcourse_id=subcourse_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='update-item')
    def update_item(self, request, *args, **kwargs):
        # Handle multipart/form-data updates via POST to avoid Django PATCH data loss issue
        return super().partial_update(request, *args, **kwargs)


class AdminMCQQuestionViewSet(BulkDeleteMixin, viewsets.ModelViewSet):
    """CRUD operations for MCQ Questions."""
    queryset = MCQQuestion.objects.all()
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        subcourse_id = self.request.query_params.get('subcourse_id')
        if subcourse_id:
            queryset = queryset.filter(subcourse_id=subcourse_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='update-item')
    def update_item(self, request, *args, **kwargs):
        # Handle multipart/form-data updates via POST
        return super().partial_update(request, *args, **kwargs)


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
        # Return all active subcourses so the app can display the curriculum for unpurchased courses
        queryset = SubCourse.objects.filter(is_active=True).order_by('priority')
        
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
        upload_type = request.data.get('type') or request.data.get('model_type')
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
                    if 'questionid' in clean_row or 'questiontext' in clean_row or 'question' in clean_row:
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
                    q_text = get_col_val(row_dict, ['Question_Text', 'Question Text', 'Question'])
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
                # Find all option indices available in the headers
                option_indices = []
                for h in headers:
                    clean_h = h.strip().lower().replace(' ', '').replace('_', '')
                    if clean_h.startswith('option'):
                        try:
                            idx = int(clean_h.replace('option', ''))
                            option_indices.append(idx)
                        except ValueError:
                            pass
                
                if not option_indices:
                    # Fallback if headers are weird, try up to 20
                    option_indices = list(range(1, 21))
                else:
                    option_indices = sorted(list(set(option_indices)))

                for row_data in target_rows:
                    row_dict = dict(zip(headers, row_data))
                    q_text = get_col_val(row_dict, ['Question_Text', 'Question Text', 'Question'])
                    if not q_text:
                        continue
                    
                    question = MCQQuestion.objects.create(
                        subcourse=subcourse,
                        text=q_text
                    )
                    
                    for i in option_indices:
                        opt_text = get_col_val(row_dict, [f'Option_{i}', f'Option {i}', f'Option{i}'])
                        opt_status = get_col_val(row_dict, [f'Status_{i}', f'Status {i}', f'Status{i}']).lower()
                        
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


class BannerViewSet(viewsets.ModelViewSet):
    """CRUD operations for Banners."""
    queryset = Banner.objects.all().order_by('-created_at')
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]
