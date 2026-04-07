from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    Product, BatteryCustomization, MaintenanceRequest, 
    TradeInRequest, SiteSettings, ContactMessage, 
    Order, Visitor, HeroSlider
)
from .serializers import (
    ProductSerializer, 
    BatteryCustomizationSerializer, 
    MaintenanceRequestSerializer, 
    TradeInRequestSerializer,
    SiteSettingsSerializer,
    ContactMessageSerializer,
    OrderSerializer,
    VisitorSerializer,
    HeroSliderSerializer
)
from .scraper import scrape_product

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    @action(detail=False, methods=['post'], url_path='scrape')
    def scrape(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = scrape_product(url)
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='sync-all')
    def sync_all(self, request):
        products = Product.objects.exclude(akakce_url__isnull=True).exclude(akakce_url='')
        results = []
        for product in products:
            try:
                res = scrape_product(product.akakce_url)
                if res['success'] and res['price'] > 0:
                    product.price = res['price']
                    product.save()
                    results.append({'id': product.id, 'success': True, 'price': res['price']})
                else:
                    results.append({'id': product.id, 'success': False, 'error': res.get('message', 'Price was 0')})
            except Exception as e:
                results.append({'id': product.id, 'success': False, 'error': str(e)})
        
        return Response({'success': True, 'results': results})

class BatteryCustomizationViewSet(viewsets.ModelViewSet):
    queryset = BatteryCustomization.objects.all().order_by('-created_at')
    serializer_class = BatteryCustomizationSerializer

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all().order_by('-created_at')
    serializer_class = MaintenanceRequestSerializer

class TradeInRequestViewSet(viewsets.ModelViewSet):
    queryset = TradeInRequest.objects.all().order_by('-created_at')
    serializer_class = TradeInRequestSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all().order_by('-created_at')
    serializer_class = VisitorSerializer

class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer

    def list(self, request, *args, **kwargs):
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

class HeroSliderViewSet(viewsets.ModelViewSet):
    queryset = HeroSlider.objects.filter(is_active=True).order_by('order', '-created_at')
    serializer_class = HeroSliderSerializer
