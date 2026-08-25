from rest_framework import serializers

from .models import Division, District, Thana


class DivisionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Division

        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Division name is required."
            )

        queryset = Division.objects.filter(
            name__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "This division already exists."
            )

        return value


class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District

        fields = [
            "id",
            "division",
            "name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "District name is required."
            )

        division = self.initial_data.get("division")

        if division:
            queryset = District.objects.filter(
                division_id=division,
                name__iexact=value,
            )

            if self.instance:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    "This district already exists in "
                    "this division."
                )

        return value


class ThanaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Thana

        fields = [
            "id",
            "district",
            "name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Thana name is required."
            )

        district = self.initial_data.get("district")

        if district:
            queryset = Thana.objects.filter(
                district_id=district,
                name__iexact=value,
            )

            if self.instance:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    "This thana already exists in "
                    "this district."
                )

        return value