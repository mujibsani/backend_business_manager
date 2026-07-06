from django.contrib import admin
from .models import Division, District, Thana


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "division")
    list_filter = ("division",)
    search_fields = ("name",)


@admin.register(Thana)
class ThanaAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    list_filter = ("district",)
    search_fields = ("name",)