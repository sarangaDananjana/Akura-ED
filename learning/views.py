import os
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

import csv
import io
from .models import Course, SubCourse, Flashcard, MCQQuestion, MCQOption
from .serializers import (
    CourseSerializer, SubCourseSerializer, FlashcardSerializer,
    MCQQuestionSerializer, MCQOptionSerializer
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

class AdminCourseViewSet(viewsets.ModelViewSet):
    """CRUD operations for Courses in Custom Admin Panel."""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminSubCourseViewSet(viewsets.ModelViewSet):
    """CRUD operations for SubCourses in Custom Admin Panel."""
    queryset = SubCourse.objects.all()
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminFlashcardViewSet(viewsets.ModelViewSet):
    """CRUD operations for Flashcards. Allows uploading text, image, voice."""
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminMCQQuestionViewSet(viewsets.ModelViewSet):
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

class ReadOnlyCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for Courses."""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReadOnlySubCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for SubCourses."""
    queryset = SubCourse.objects.filter(is_active=True)
    serializer_class = SubCourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReadOnlyFlashcardViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for Flashcards."""
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReadOnlyMCQQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only operations for MCQ Questions."""
    queryset = MCQQuestion.objects.all()
    serializer_class = MCQQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


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
            # Read and decode CSV
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            rows = list(reader)

            # Find the header row (assuming it contains 'Question_ID' or 'Question_Text')
            header_idx = -1
            for idx, row in enumerate(rows):
                if row and any(cell.strip().lower() == 'question_id' for cell in row):
                    header_idx = idx
                    break
            
            if header_idx == -1:
                return Response({"error": "Could not find header row containing 'Question_ID'."}, status=status.HTTP_400_BAD_REQUEST)

            headers = [h.strip() for h in rows[header_idx]]
            data_rows = rows[header_idx + 1:]

            if end_row == -1 or end_row > len(data_rows):
                end_row = len(data_rows)
            
            if start_row < 1:
                start_row = 1

            # Slicing the data rows (start_row is 1-based index)
            target_rows = data_rows[start_row - 1 : end_row]

            created_count = 0

            if upload_type == 'flashcard':
                for row_data in target_rows:
                    row_dict = dict(zip(headers, row_data))
                    q_text = row_dict.get('Question_Text', '').strip()
                    ans_text = row_dict.get('Correct_Description', '').strip()

                    if q_text and ans_text:
                        Flashcard.objects.create(
                            subcourse=subcourse,
                            question_text=q_text,
                            answer_text=ans_text
                        )
                        created_count += 1
                        
            elif upload_type == 'mcq':
                for row_data in target_rows:
                    row_dict = dict(zip(headers, row_data))
                    q_text = row_dict.get('Question_Text', '').strip()
                    if not q_text:
                        continue
                    
                    question = MCQQuestion.objects.create(
                        subcourse=subcourse,
                        text=q_text
                    )
                    
                    for i in range(1, 6):
                        opt_text = row_dict.get(f'Option_{i}', '').strip()
                        opt_status = row_dict.get(f'Status_{i}', '').strip().lower()
                        
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
