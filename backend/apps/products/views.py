from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin

from .models import Product, ProductVariant
from .serializers import ProductSerializer, ProductVariantCreateSerializer, ProductVariantSerializer


def _error(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({"data": None, "error": message}, status=code)


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        products = Product.objects.prefetch_related("variants").all()
        search = request.query_params.get("search", "").strip()
        if search:
            products = products.filter(name__icontains=search)
        return Response({"data": ProductSerializer(products, many=True).data, "error": None})

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return _error(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(
            {"data": ProductSerializer(serializer.save()).data, "error": None},
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        return Product.objects.prefetch_related("variants").get(pk=pk)

    def get(self, request, pk):
        try:
            product = self.get_object(pk)
        except Product.DoesNotExist:
            return _error("Product not found.", status.HTTP_404_NOT_FOUND)
        return Response({"data": ProductSerializer(product).data, "error": None})

    def put(self, request, pk):
        try:
            product = self.get_object(pk)
        except Product.DoesNotExist:
            return _error("Product not found.", status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if not serializer.is_valid():
            return _error(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response({"data": ProductSerializer(serializer.save()).data, "error": None})

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return _error("Product not found.", status.HTTP_404_NOT_FOUND)
        try:
            product.delete()
        except IntegrityError:
            return _error("Product cannot be deleted because it is in use.", status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductVariantListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, product_pk):
        try:
            Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return _error("Product not found.", status.HTTP_404_NOT_FOUND)
        variants = ProductVariant.objects.filter(product_id=product_pk)
        return Response({"data": ProductVariantSerializer(variants, many=True).data, "error": None})

    def post(self, request, product_pk):
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return _error("Product not found.", status.HTTP_404_NOT_FOUND)
        serializer = ProductVariantCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            variant = serializer.save(product=product)
        except IntegrityError:
            return _error("A variant with this name already exists for the product.")
        return Response(
            {"data": ProductVariantSerializer(variant).data, "error": None},
            status=status.HTTP_201_CREATED,
        )


class ProductVariantDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, product_pk, pk):
        return ProductVariant.objects.select_related("product").get(product_id=product_pk, pk=pk)

    def put(self, request, product_pk, pk):
        try:
            variant = self.get_object(product_pk, pk)
        except ProductVariant.DoesNotExist:
            return _error("Variant not found.", status.HTTP_404_NOT_FOUND)
        serializer = ProductVariantCreateSerializer(variant, data=request.data)
        if not serializer.is_valid():
            return _error(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            variant = serializer.save()
        except IntegrityError:
            return _error("A variant with this name already exists for the product.")
        return Response({"data": ProductVariantSerializer(variant).data, "error": None})

    def delete(self, request, product_pk, pk):
        try:
            variant = self.get_object(product_pk, pk)
        except ProductVariant.DoesNotExist:
            return _error("Variant not found.", status.HTTP_404_NOT_FOUND)
        variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
