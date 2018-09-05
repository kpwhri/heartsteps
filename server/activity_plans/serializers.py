from rest_framework import serializers
from activity_plans.model import ActivityPlan


class ActivityPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = models.ForeignKey(User)
    activity_date = models.DateField()
    start_time = models.CharField(max_length=15)
    activity_type = models.CharField(max_length=50)
    intensity = models.CharField(max_length=1, choices=INTENSITY)
    duration = models.IntegerField()
    complete = models.BooleanField(default=False)
    enjoyed = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create(self, validated_data):
        """
        Create and return a new `ActivityPlan` instance,
        given the validated data.
        """
        return ActivityPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `ActivityPlan` instance,
        given the validated data.
        """
        instance.activity_date = validated_data.get('activity_date', instance.activity_date)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.activity_type = validated_data.get('activity_type', instance.activity_type)
        instance.intensity = validated_data.get('intensity', instance.intensity)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.complete = validated_data.get('complete', instance.complete)
        instance.enjoyed = validated_data.get('enjoyed', instance.enjoyed)
        instance.save()
        return instance
