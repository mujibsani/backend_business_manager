# from django.shortcuts import render

# from rest_framework.views import APIView
# from rest_framework.response import Response

# from .services import get_customer_ledger, get_supplier_ledger


# class CustomerLedgerAPIView(APIView):

#     def get(self, request, name):

#         data = get_customer_ledger(name)

#         return Response({
#             "customer": name,
#             "ledger": data
#         })
    

# class SupplierLedgerAPIView(APIView):

#     def get(self, request, name):

#         data = get_supplier_ledger(name)

#         return Response({
#             "supplier": name,
#             "ledger": data
#         })
    

