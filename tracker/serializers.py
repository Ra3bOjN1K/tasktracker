from rest_framework import serializers

from tracker.models import Task


class TaskSerializers(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    executors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'created', 'creator',
                  'get_verbose_status_val', 'executors', 'description')
