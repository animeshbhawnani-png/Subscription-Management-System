from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Customer
from .serializers import CustomerSerializer
from apps.users.permissions import IsAdminOrStaff


def _ok(data): return Response({"data": data, "error": None})
def _created(data): return Response({"data": data, "error": None}, status=status.HTTP_201_CREATED)
def _err(msg, code=400): return Response({"data": None, "error": msg}, status=code)


class CustomerListCreateView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        qs = Customer.objects.filter(is_active=True)
        return _ok(CustomerSerializer(qs, many=True).data)

    def post(self, request):
        s = CustomerSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors, 422)
        s.save()
        return _created(s.data)


class CustomerDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, pk):
        c = get_object_or_404(Customer, pk=pk)
        return _ok(CustomerSerializer(c).data)

    def put(self, request, pk):
        c = get_object_or_404(Customer, pk=pk)
        s = CustomerSerializer(c, data=request.data, partial=True)
        if not s.is_valid():
            return _err(s.errors, 422)
        s.save()
        return _ok(s.data)
