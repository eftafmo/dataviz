from rest_framework import serializers
from .models import ProjectAllocation


class ProjectSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='project.code')
    name = serializers.CharField(source='project.name')
    allocation = serializers.DecimalField(source='total_allocation', max_digits=15, decimal_places=2)
    nuts = serializers.CharField(source='project.nuts_id')
    programme = serializers.CharField(source='project.programme_id')
    url = serializers.CharField(source='project.url')

    class Meta:
        model = ProjectAllocation
        fields = (
            'code',
            'name',
            'allocation',
            'state',
            'nuts',
            'programme',
            # 'outcome',  # TODO check if it's used
            'url',
        )
