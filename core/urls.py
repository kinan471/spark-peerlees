from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, BatteryCustomizationViewSet, MaintenanceRequestViewSet, 
    TradeInRequestViewSet, SiteSettingsViewSet, ContactMessageViewSet, 
    OrderViewSet, VisitorViewSet, HeroSliderViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'settings', SiteSettingsViewSet, basename='settings')
# ... (سجل باقي الـ ViewSets هنا)

urlpatterns = [
    # هذا السطر يربط الدالة مباشرة بـ /api/scrape/
    path('scrape/', ProductViewSet.as_view({'post': 'scrape', 'get': 'scrape'}), name='direct-scrape'),
    path('', include(router.urls)),
]
