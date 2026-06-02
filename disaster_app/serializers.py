from rest_framework import serializers
from .models import (
    Incident,
    HazardImage,
    SensorData,
    HazardReport
)


# =========================================================
# HAZARD IMAGE SERIALIZER
# =========================================================
class HazardImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = HazardImage
        fields = '__all__'


# =========================================================
# INCIDENT SERIALIZER
# =========================================================
class IncidentSerializer(serializers.ModelSerializer):

    images = HazardImageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Incident
        fields = '__all__'


# =========================================================
# SENSOR DATA SERIALIZER
# =========================================================
class SensorSerializer(serializers.ModelSerializer):

    class Meta:
        model = SensorData
        fields = '__all__'


# =========================================================
# HAZARD REPORT SERIALIZER
# =========================================================
class HazardReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = HazardReport
        fields = '__all__'
        read_only_fields = (
            'reported_by',
            'created_at',
        )