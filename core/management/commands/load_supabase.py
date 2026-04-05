import json
import os
from django.core.management.base import BaseCommand
from core.models import Product, Message, Setting, Visit, Order
from django.utils.dateparse import parse_datetime

from django.conf import settings

class Command(BaseCommand):
    help = 'Load data from Supabase JSON export'

    def handle(self, *args, **options):
        # File path relative to the root of the project
        file_path = os.path.join(settings.BASE_DIR.parent, 'temp_data', 'supabase_export.json')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Export file not found at {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Settings
        for item in data.get('settings', []):
            Setting.objects.update_or_create(
                id=item['id'],
                defaults={
                    'site_name': item.get('site_name', ''),
                    'tagline': item.get('tagline', ''),
                    'whatsapp_number': item.get('whatsapp_number', ''),
                    'primary_color': item.get('primary_color', ''),
                    'secondary_color': item.get('secondary_color', ''),
                    'dark_mode': item.get('dark_mode', False),
                    'language': item.get('language', 'ar'),
                }
            )
        self.stdout.write(self.style.SUCCESS('Settings migrated'))

        # 2. Products
        for item in data.get('products', []):
            Product.objects.update_or_create(
                id=item['id'],
                defaults={
                    'name_ar': item.get('name_ar', ''),
                    'name_tr': item.get('name_tr', ''),
                    'price': item.get('price', 0),
                    'image_url': item.get('image_url', ''),
                    'description_ar': item.get('description_ar', ''),
                    'description_tr': item.get('description_tr', ''),
                    'category': item.get('category', 'ebike'),
                    'stock': item.get('stock', 1),
                    'akakce_url': item.get('akakce_url', ''),
                    'meta_title': item.get('meta_title', ''),
                    'meta_description': item.get('meta_description', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'{len(data.get("products", []))} Products migrated'))

        # 3. Messages
        for item in data.get('messages', []):
            Message.objects.get_or_create(
                id=item['id'],
                defaults={
                    'name': item.get('name', ''),
                    'email': item.get('email', ''),
                    'subject': item.get('subject', ''),
                    'message': item.get('message', ''),
                    'replied': item.get('replied', False),
                }
            )

        # 4. Visits
        for item in data.get('visits', []):
            Visit.objects.get_or_create(
                id=item['id'],
                defaults={
                    'path': item.get('path', ''),
                    'user_agent': item.get('user_agent', ''),
                    'referrer': item.get('referrer', ''),
                }
            )

        # 5. Orders
        for item in data.get('orders', []):
            product = None
            if item.get('product_id'):
                try:
                    product = Product.objects.get(id=item['product_id'])
                except Product.DoesNotExist:
                    pass
            
            Order.objects.get_or_create(
                id=item['id'],
                defaults={
                    'product': product,
                    'customer_name': item.get('customer_name', ''),
                    'customer_phone': item.get('customer_phone', ''),
                    'status': item.get('status', 'pending'),
                }
            )

        self.stdout.write(self.style.SUCCESS('Migration from Supabase JSON completed!'))
