import django_filters
from .models import WeatherRecord, WeatherStatistics

class WeatherRecordFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="record_date", lookup_expr="gte")
    date_to   = django_filters.DateFilter(field_name="record_date", lookup_expr="lte")
    station_id = django_filters.NumberFilter(field_name="station_id")  # via FK column

    class Meta:
        model = WeatherRecord
        fields = ["station_id", "date_from", "date_to"]


class WeatherStatisticsFilter(django_filters.FilterSet):
    year_from = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_to   = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    station_id = django_filters.NumberFilter(field_name="station_id")

    class Meta:
        model = WeatherStatistics
        fields = ["station_id", "year_from", "year_to"]
