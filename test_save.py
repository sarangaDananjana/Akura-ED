import os, sys, django
sys.path.append(r'c:\Users\Saranga\Desktop\Akura ED')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from learning.models import SubCourse, Flashcard

# Create a test SubCourse
sc, _ = SubCourse.objects.get_or_create(title="Test SC")

# create file
img = SimpleUploadedFile("test_img.jpg", b"file_content", content_type="image/jpeg")

fc = Flashcard.objects.create(
    subcourse=sc,
    question_text="Test",
    answer_text="Test ans",
    question_image=img
)
print("Created flashcard with id", fc.id)
print("Image path:", fc.question_image.name)
