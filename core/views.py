from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Message, Setting, Visit, Order
from .serializers import ProductSerializer, MessageSerializer, SettingSerializer, VisitSerializer, OrderSerializer
from .scraper import scrape_product

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_serializer = ProductSerializer # wait, serializer_class
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

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    
    def get_object(self):
        return Setting.objects.get_or_create(id='default')[0]
    
    @action(detail=False, methods=['get', 'patch'], url_path='current')
    def current(self, request):
        setting = self.get_object()
        if request.method == 'PATCH':
            serializer = self.get_serializer(setting, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
        serializer = self.get_serializer(setting)
        return Response(serializer.data)

class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-created_at')
    serializer_class = VisitSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
