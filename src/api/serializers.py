from rest_framework import serializers
from .models import WeatherRecord, WeatherStatistics, WeatherStation

class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = ("station_id", "station_code", "state")

class WeatherRecordSerializer(serializers.ModelSerializer):
    station = WeatherStationSerializer(read_only=True)
    max_temp_c = serializers.SerializerMethodField()
    min_temp_c = serializers.SerializerMethodField()
    precipitation_mm = serializers.SerializerMethodField()

    def get_max_temp_c(self, obj):
        return None if obj.max_temp is None else round(obj.max_temp / 10.0, 1)

    def get_min_temp_c(self, obj):
        return None if obj.min_temp is None else round(obj.min_temp / 10.0, 1)

    def get_precipitation_mm(self, obj):
        return None if obj.precipitation is None else round(obj.precipitation / 10.0, 1)

    class Meta:
        model = WeatherRecord
        fields = (
            "record_id", "record_date", "station",
            "max_temp", "min_temp", "precipitation",
            "max_temp_c", "min_temp_c", "precipitation_mm",
        )

class WeatherStatisticsSerializer(serializers.ModelSerializer):
    station = WeatherStationSerializer(read_only=True)

    class Meta:
        model = WeatherStatistics
        fields = (
            "station", "year",
            "avg_max_temp_celsius", "avg_min_temp_celsius", "total_precipitation_cm",
        )
