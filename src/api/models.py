from django.db import models

class WeatherStation(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_code = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=2)

    class Meta:
        db_table = "weather_station"
        managed = False 

    def __str__(self):
        return f"{self.station_code} ({self.state})"


class WeatherRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    station = models.ForeignKey(WeatherStation, on_delete=models.DO_NOTHING, db_column="station_id")
    record_date = models.DateField()
    max_temp = models.IntegerField(null=True, blank=True)      
    min_temp = models.IntegerField(null=True, blank=True)     
    precipitation = models.IntegerField(null=True, blank=True)  

    class Meta:
        db_table = "weather_record"
        managed = False
        unique_together = (("station", "record_date"),)
        indexes = [
            models.Index(fields=["station", "record_date"]),
        ]


class WeatherStatistics(models.Model):
    station = models.ForeignKey(WeatherStation, on_delete=models.DO_NOTHING, db_column="station_id", primary_key=True)
    year = models.IntegerField()
    avg_max_temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_min_temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_precipitation_cm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "weather_statistics"
        managed = False
        unique_together = (("station", "year"),)
        indexes = [
            models.Index(fields=["station", "year"]),
        ]
