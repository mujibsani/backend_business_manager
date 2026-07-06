from rest_framework.views import APIView
from rest_framework.response import Response

from .services import (
    get_dashboard_data,
    get_profit_summary,
    get_daily_sales,
    get_weekly_sales,
    get_monthly_sales
)



class DashboardAPIView(APIView):

    def get(self, request):

        return Response({
            "dashboard": get_dashboard_data(),
            "profit": get_profit_summary(),
            "charts": {
                "daily_sales": get_daily_sales(),
                "weekly_sales": get_weekly_sales(),
                "monthly_sales": get_monthly_sales(),
            }
        })
    
