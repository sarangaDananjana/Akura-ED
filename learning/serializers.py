from rest_framework import serializers
from .models import Domain, Course, SubCourse, Flashcard, MCQQuestion, MCQOption, Enrollment

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class ShopCourseSerializer(serializers.ModelSerializer):
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
    
    def get_is_purchased(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.enrollments.filter(user=user).exists()


class SubCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCourse
        fields = '__all__'


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'


class MCQOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQOption
        fields = '__all__'


class MCQQuestionSerializer(serializers.ModelSerializer):
    # Nested serializer to fetch options alongside the question in the admin panel
    options = MCQOptionSerializer(many=True, read_only=True)
    
    incoming_options = serializers.JSONField(
        write_only=True,
        required=False
    )

    class Meta:
        model = MCQQuestion
        fields = '__all__'

    def create(self, validated_data):
        options_data = validated_data.pop('incoming_options', [])
        if isinstance(options_data, str):
            import json
            try:
                options_data = json.loads(options_data)
            except Exception:
                options_data = []
        question = super().create(validated_data)
        for opt in options_data:
            MCQOption.objects.create(
                question=question,
                text=opt.get('text', ''),
                is_correct=opt.get('is_correct', False)
            )
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('incoming_options', None)
        if isinstance(options_data, str):
            import json
            try:
                options_data = json.loads(options_data)
            except Exception:
                options_data = []
        question = super().update(instance, validated_data)
        
        if options_data is not None:
            # Delete old options and recreate
            question.options.all().delete()
            for opt in options_data:
                MCQOption.objects.create(
                    question=question,
                    text=opt.get('text', ''),
                    is_correct=opt.get('is_correct', False)
                )
        return question


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
