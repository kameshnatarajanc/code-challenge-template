from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter

from .models import WeatherRecord, WeatherStatistics
from .serializers import WeatherRecordSerializer, WeatherStatisticsSerializer
from .filters import WeatherRecordFilter, WeatherStatisticsFilter
from django_filters.rest_framework import DjangoFilterBackend

class WeatherRecordListView(ListAPIView):
    queryset = WeatherRecord.objects.select_related("station").all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WeatherRecordFilter
    ordering_fields = ["record_date", "station_id"]
    ordering = ["record_date"]

class WeatherStatisticsListView(ListAPIView):
    queryset = WeatherStatistics.objects.select_related("station").all()
    serializer_class = WeatherStatisticsSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WeatherStatisticsFilter
    ordering_fields = ["year", "station_id"]
    ordering = ["year"]




def root_index(_request):
    return JsonResponse({
        "message": "Weather API",
        "docs": "/api/docs/",
        "endpoints": ["/api/weather", "/api/weather/stats"]
    })