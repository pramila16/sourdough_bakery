from rest_framework import serializers
class BakeryItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = serializers.IntegerField()

class BakingScheduleSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    bakery_item = serializers.CharField()
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=['pending', 'in_progress', 'completed'], default='pending')
    quantity = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class IngredientSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    quantity_in_stock = serializers.IntegerField()
    unit = serializers.CharField(max_length=20)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(max_length=255)
    bakery_item_id = serializers.CharField()  # Expecting BakeryItem ID
    quantity = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['pending', 'completed'], default='pending')
