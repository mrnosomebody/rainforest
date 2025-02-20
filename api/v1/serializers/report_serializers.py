from rest_framework import serializers


class ReportCreateSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError("start_date must be before end_date.")
        return data


class ReportResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    result = serializers.JSONField(required=False, allow_null=True)
