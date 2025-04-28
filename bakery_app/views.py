from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from rest_framework.exceptions import NotFound
from bson import ObjectId

from .models import BakeryItem, Order
from .serializers import BakeryItemSerializer,OrderSerializer
from rest_framework.permissions import IsAuthenticated

"""
Security Considerations:
- Only authenticated users can perform CRUD operations.
- Users should only access their own orders (future enhancement).
- Input validation must be strict to avoid injection attacks.
- Soft-deletion is used to avoid accidental data loss.
"""


class BakeryItemViewSet(viewsets.ModelViewSet):
    serializer_class = BakeryItemSerializer
    #permission_classes = [IsAuthenticated] -> Only authenticated users can perform CRUD operations

    def get_queryset(self):
        return BakeryItem.objects.all()

    def get_object(self):
        object_id = ObjectId(self.kwargs['pk'])
        try:
            obj = BakeryItem.objects.get(id=object_id, is_deleted=False)
        except BakeryItem.DoesNotExist:
            raise NotFound(detail="Bakery item not found or already deleted")
        return obj

    def create(self, request, *args, **kwargs):
        validated_data = request.data
        bakery_item = BakeryItem(**validated_data)
        bakery_item.save()
        return Response(self.get_serializer(bakery_item).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_deleted:
            return Response({"detail": "Cannot update a deleted item."}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = request.data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_deleted:
            return Response({"detail": "Cannot update a deleted item."}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = request.data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(is_deleted=False)

    def get_object(self):
        object_id = ObjectId(self.kwargs['pk'])
        try:
            obj = Order.objects.get(id=object_id, is_deleted=False)
        except Order.DoesNotExist:
            raise NotFound(detail="Order not found or already deleted")
        return obj

    def create(self, request, *args, **kwargs):
        validated_data = request.data
        order = Order(**validated_data)
        order.save()
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_deleted:
            return Response({"detail": "Cannot update a deleted order."}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = request.data
        for attr, value in validated_data.items():
            if attr == "bakery_item_id":
                try:
                    value = ObjectId(value)
                except Exception as e:
                    return Response(f'{"detail": "Invalid bakery_item_id format. ", {str(e)}}', status=status.HTTP_400_BAD_REQUEST)
            setattr(instance, attr, value)
        instance.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        """
        Partial update an Order safely with version conflict detection.
        """
        try:
            order = self.get_object()  # Handles 404 automatically if object not found
        except Http404:
            return Response({"detail": "Order not found or has been deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not request.data:
            return Response({"detail": "No fields provided to update."}, status=status.HTTP_400_BAD_REQUEST)

        request_version = request.data.get('version')
        if request_version is None:
            return Response({"detail": "Version field is required for conflict detection."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            request_version = int(request_version)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid version format."}, status=status.HTTP_400_BAD_REQUEST)

        if request_version != order.version:
            return Response(
                {"detail": "Conflict detected, the order has been modified by another user."},
                status=status.HTTP_409_CONFLICT
            )

        allowed_fields = {'customer_name', 'quantity', 'status','bakery_item_id' }  # Only allow updating specific fields
        for field, value in request.data.items():
            if field == 'version':
                continue  # Skip version, handled separately
            if field not in allowed_fields:
                return Response({"detail": f"Invalid or not allowed field: {field}"},
                                status=status.HTTP_400_BAD_REQUEST)
            if field == 'bakery_item_id':
                value = ObjectId(value)
            setattr(order, field, value)

        order.version += 1

        order.save()

        return Response({"detail": f"Order {str(order.id)} updated successfully."}, status=status.HTTP_200_OK)