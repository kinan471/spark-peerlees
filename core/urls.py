from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, MessageViewSet, SettingViewSet, VisitViewSet, OrderViewSet
from .upload_views import ImageUploadView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'settings', SettingViewSet, basename='setting')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('', include(router.urls)),
]
