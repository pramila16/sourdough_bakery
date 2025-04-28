from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BakeryItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'bakery-items', BakeryItemViewSet, basename="bakeryitem")
router.register(r'orders', OrderViewSet,basename="orders" )

urlpatterns = [
    path('', include(router.urls)),
]