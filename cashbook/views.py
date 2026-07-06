from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import get_cashbook_summary
from .models import CashbookEntry


class CashbookAPIView(APIView):

    def get(self, request):

        entries = CashbookEntry.objects.all().order_by("-date")

        data = [
            {
                "date": e.date,
                "type": e.entry_type,
                "amount": e.amount,
                "description": e.description
            }
            for e in entries
        ]

        return Response({
            "summary": get_cashbook_summary(),
            "entries": data
        })