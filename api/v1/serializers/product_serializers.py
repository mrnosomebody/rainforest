from rest_framework import serializers

from products.models import Product


class ProductReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "cost",
            "description",
            "created_at",
            "updated_at",
            "stock",
        ]
        read_only_fields = fields


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price", "cost", "description", "stock"]


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price", "cost", "description", "stock", "hidden"]
