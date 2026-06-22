import os, sys, django
sys.path.append(r'c:\Users\Saranga\Desktop\Akura ED')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from learning.models import Flashcard, MCQQuestion

fc = Flashcard.objects.exclude(question_image='').first()
print('Flashcard with image:', fc.id if fc else 'None')
if fc:
    print('URL:', fc.question_image.url if fc.question_image else 'No url')
    print('Raw value:', fc.question_image.name)

mc = MCQQuestion.objects.exclude(image='').first()
print('MCQ with image:', mc.id if mc else 'None')
if mc:
    print('URL:', mc.image.url if mc.image else 'No url')
    print('Raw value:', mc.image.name)
