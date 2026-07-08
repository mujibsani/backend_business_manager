from rest_framework.response import Response
from rest_framework.views import APIView

from reports.services import get_dashboard_summary


class DashboardAPIView(APIView):
    """
    Dashboard Summary Report
    """

    def get(self, request):

        return Response(
            get_dashboard_summary()
        )