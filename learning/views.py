import os
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SubCourse, Flashcard, MCQQuestion, MCQOption
from .serializers import (
    SubCourseSerializer, FlashcardSerializer,
    MCQQuestionSerializer, MCQOptionSerializer
)

# Initialize MongoClient globally for connection pooling across requests
MONGO_URI = os.getenv('MONGO_URI')
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None

# Select the specific MongoDB database to use
mongo_db = mongo_client['edtech_progress_db'] if mongo_client else None


class SyncProgressView(APIView):
    """
    API endpoint for the Flutter mobile app to bulk sync offline-first 
    MCQ and Flashcard progress directly to MongoDB Atlas.
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

        # Expected Payload Example:
        # {
        #   "mcq_answers": {"q001": 3, "q005": 1},
        #   "flashcards": [
        #       {
        #           "flashcard_id": 10,
        #           "status": "learning",
        #           "next_review": "2023-11-20T10:00:00Z",
        #           "interaction": {"ease": 2.5, "interval": 1, "date": "2023-11-19T10:00:00Z"}
        #       }
        #   ]
        # }

        mcq_answers = data.get('mcq_answers', {})
        flashcards_data = data.get('flashcards', [])

        mcq_operations = []
        flashcard_operations = []
        now = datetime.utcnow()

        # 1. Prepare MCQ updates (Dot notation for specific answers)
        if mcq_answers:
            set_fields = {'last_updated': now}
            for q_id, answer in mcq_answers.items():
                set_fields[f'answers.{q_id}'] = answer

            mcq_operations.append(
                UpdateOne(
                    {'user_id': user_id},
                    {'$set': set_fields},
                    upsert=True
                )
            )

        # 2. Prepare Flashcard updates ($push with $each & $slice)
        for fc in flashcards_data:
            fc_id = fc.get('flashcard_id')
            if not fc_id:
                continue

            update_doc = {
                '$set': {
                    'status': fc.get('status'),
                    'next_review': fc.get('next_review'),
                    'last_updated': now
                }
            }

            interaction = fc.get('interaction')
            if interaction:
                update_doc['$push'] = {
                    'history': {
                        '$each': [interaction],
                        '$slice': -3  # Automatically limits the history array to the 3 most recent records
                    }
                }

            flashcard_operations.append(
                UpdateOne(
                    {'user_id': user_id, 'flashcard_id': fc_id},
                    update_doc,
                    upsert=True
                )
            )

        # 3. Execute Bulk Writes
        results = {}
        try:
            if mcq_operations:
                # Execution with ordered=False allows parallelism and avoids aborting on individual errors
                res_mcq = mongo_db['mcq_progress'].bulk_write(
                    mcq_operations, ordered=False)
                results['mcqs'] = {
                    "matched": res_mcq.matched_count,
                    "modified": res_mcq.modified_count,
                    "upserted": res_mcq.upserted_count
                }

            if flashcard_operations:
                res_fc = mongo_db['flashcard_progress'].bulk_write(
                    flashcard_operations, ordered=False)
                results['flashcards'] = {
                    "matched": res_fc.matched_count,
                    "modified": res_fc.modified_count,
                    "upserted": res_fc.upserted_count
                }

            return Response({
                "message": "Progress synced successfully",
                "details": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Custom Admin Panel Views ---
# All views here require the user to have an Admin account (is_staff=True)


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
