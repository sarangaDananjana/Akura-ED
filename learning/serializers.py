from rest_framework import serializers
from .models import Course, SubCourse, Flashcard, MCQQuestion, MCQOption

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


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
    
    incoming_options = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = MCQQuestion
        fields = '__all__'

    def create(self, validated_data):
        options_data = validated_data.pop('incoming_options', [])
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
