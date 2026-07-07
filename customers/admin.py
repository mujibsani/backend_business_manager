from django.contrib import admin
from .models import Customer
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Customer


class CustomerForm(ModelForm):

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if Customer.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number already exists!")

        return phone

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "division",
        "district",
        "thana",
        "area",
        "opening_balance",
        "opening_balance_type",
        "is_active",
    )

    list_filter = (
        "division",
        "district",
        "thana",
        "opening_balance_type",
        "is_active",
    )

    search_fields = (
        "name",
        "phone",
        "area",
    )

    ordering = (
        "name",
    )