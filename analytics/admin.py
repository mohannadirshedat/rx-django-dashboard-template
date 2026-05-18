from django.contrib import admin

from .models import DailyMetric, DeviceShare, KpiSnapshot


@admin.register(KpiSnapshot)
class KpiSnapshotAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "previous_value", "updated_at")


@admin.register(DailyMetric)
class DailyMetricAdmin(admin.ModelAdmin):
    list_display = ("metric_type", "date", "value")
    list_filter = ("metric_type",)


@admin.register(DeviceShare)
class DeviceShareAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "period", "fill")
    list_filter = ("period",)
