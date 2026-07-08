from django.apps import AppConfig


class SalesReturnsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales_returns"

    def ready(self):
        import sales_returns.signals