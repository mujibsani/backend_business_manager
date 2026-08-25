from rest_framework.views import APIView
from rest_framework.response import Response

from .services import get_cashbook_summary
from .models import CashbookEntry

from core.permissions import IsAdminOrManager


class CashbookAPIView(APIView):
    """
    Cashbook is read-only.

    ADMIN:
        Full visibility.

    MANAGER:
        Full visibility.

    STAFF:
        No access.
    """

    permission_classes = [IsAdminOrManager]

    def get(self, request):

        entries = (
            CashbookEntry.objects
            .all()
            .order_by("-date", "-id")
        )

        data = [
            {
                "id": entry.id,
                "date": entry.date,
                "type": entry.entry_type,
                "source_type": entry.source_type,
                "amount": entry.amount,
                "reference": entry.reference,
                "description": entry.description,
            }
            for entry in entries
        ]

        return Response({
            "summary": get_cashbook_summary(),
            "entries": data,
        })