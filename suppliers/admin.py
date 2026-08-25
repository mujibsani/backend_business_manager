from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = "__all__"

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        queryset = Supplier.objects.filter(
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

    def clean_opening_balance(self):

        balance = self.cleaned_data[
            "opening_balance"
        ]

        if balance < 0:
            raise ValidationError(
                "Opening balance cannot be negative."
            )

        return balance


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    form = SupplierForm

    list_display = (
        "id",
        "name",
        "phone",
        "district",
        "thana",
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
        "division",
        "district",
        "thana",
        "area",
        "address",
    )

    ordering = (
        "name",
    )