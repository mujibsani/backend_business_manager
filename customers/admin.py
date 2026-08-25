from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = "__all__"

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        queryset = Customer.objects.filter(
            phone=phone
        )

        if self.instance and self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise ValidationError(
                "This phone number already exists!"
            )

        return phone


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    form = CustomerForm

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
        "email",
        "area",
        "address",
    )

    ordering = (
        "name",
    )