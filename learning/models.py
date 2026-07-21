from django.db import models
from django.conf import settings
from users.models import CustomUser


class Domain(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Priority for ordering. Lower numbers appear first.")

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.title


class Course(models.Model):
    domain = models.ForeignKey(Domain, related_name='courses', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255,default="none")
    description = models.TextField(blank=True, default="none")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price of the course.")
    icon = models.CharField(max_length=100, blank=True, null=True)
    teachers = models.ManyToManyField(CustomUser, related_name='taught_courses', limit_choices_to={'role': 'teacher'}, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Priority for ordering. Lower numbers appear first.")

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.title


class SubCourse(models.Model):
    course = models.ForeignKey(Course, related_name='subcourses', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_free = models.BooleanField(default=False, help_text="If True, this sub-course is free even if the parent course is paid.")
    icon = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Priority for ordering. Lower numbers appear first.")

    class Meta:
        ordering = ['priority']

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
    answer = models.TextField(blank=True, null=True)
    answer_text = models.TextField(blank=True, null=True)
    answer_image = models.ImageField(
        upload_to='flashcards/images/', blank=True, null=True)
    answer_voice = models.FileField(
        upload_to='flashcards/audio/', blank=True, null=True)

    order = models.IntegerField(default=0, help_text="Order in the sequence")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Flashcard: {self.question_text[:30]}"


class MCQQuestion(models.Model):
    """Used for evaluating flashcard knowledge after 5 cards."""
    subcourse = models.ForeignKey(
        SubCourse, related_name='mcqs', on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='mcqs/images/', blank=True, null=True)
    voice = models.FileField(upload_to='mcqs/audio/', blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"MCQ: {self.text[:30]}"


class MCQOption(models.Model):
    """Dynamic options allowing admin to add/remove rows easily."""
    question = models.ForeignKey(
        MCQQuestion, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='mcqs/options/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Option for {self.question.id}"

class Enrollment(models.Model):
    """Tracks which user is enrolled in which course or sub-course."""
    user = models.ForeignKey(CustomUser, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE, null=True, blank=True)
    subcourse = models.ForeignKey(SubCourse, related_name='enrollments', on_delete=models.CASCADE, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        # User shouldn't be enrolled multiple times in the exact same configuration
        unique_together = ('user', 'course', 'subcourse')

    def __str__(self):
        target = self.course.title if self.course else (self.subcourse.title if self.subcourse else "Unknown")
        return f"{self.user.username} enrolled in {target}"


class Banner(models.Model):
    """Model to store banners for the application."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, related_name='questions', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, related_name='asked_questions', on_delete=models.CASCADE)
    text = models.TextField()
    is_answered = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Question by {self.student.username} on {self.course.title}"

class LearningTree(models.Model):
    tree_name = models.CharField(max_length=255)
    tree_month = models.CharField(max_length=100)
    tree_file = models.FileField(upload_to='learning_trees/')

    def __str__(self):
        return f"{self.tree_name} - {self.tree_month}"
