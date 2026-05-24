from django.db import models
from django.conf import settings


class SubCourse(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Flashcard(models.Model):
    subcourse = models.ForeignKey(
        SubCourse, related_name='flashcards', on_delete=models.CASCADE)

    # Question fields (supports multi-media data entry)
    question_text = models.TextField()
    question_image = models.ImageField(
        upload_to='flashcards/images/', blank=True, null=True)
    question_voice = models.FileField(
        upload_to='flashcards/audio/', blank=True, null=True)

    # Answer fields
    answer_text = models.TextField()

    # Premium check (e.g., first 50 are free, rest are premium)
    is_premium_only = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Order in the sequence")

    def __str__(self):
        return f"Flashcard: {self.question_text[:30]}"


class MCQQuestion(models.Model):
    """Used for evaluating flashcard knowledge after 5 cards."""
    subcourse = models.ForeignKey(
        SubCourse, related_name='mcqs', on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='mcqs/images/', blank=True, null=True)
    voice = models.FileField(upload_to='mcqs/audio/', blank=True, null=True)

    def __str__(self):
        return f"MCQ: {self.text[:30]}"


class MCQOption(models.Model):
    """Dynamic options allowing admin to add/remove rows easily."""
    question = models.ForeignKey(
        MCQQuestion, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='mcqs/options/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option for {self.question.id}"
