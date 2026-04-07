from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, BatteryCustomizationViewSet, 
    MaintenanceRequestViewSet, TradeInRequestViewSet, 
    SiteSettingsViewSet, ContactMessageViewSet, 
    OrderViewSet, VisitorViewSet, HeroSliderViewSet
)
from .upload_views import ImageUploadView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'battery-customization', BatteryCustomizationViewSet, basename='battery-customization')
router.register(r'maintenance', MaintenanceRequestViewSet, basename='maintenance')
router.register(r'trade-in', TradeInRequestViewSet, basename='trade-in')
router.register(r'messages', ContactMessageViewSet, basename='message')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'settings', SiteSettingsViewSet, basename='settings')
router.register(r'hero-sliders', HeroSliderViewSet, basename='hero-sliders')

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('', include(router.urls)),
]
