from django.contrib import admin
from .models import Product, Message, Setting, Visit, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'price', 'category', 'stock')
    search_fields = ('name_ar', 'name_tr')
    
    # Priority for URL input
    fields = (
        'akakce_url', 
        'name_ar', 
        'name_tr', 
        'price', 
        'image_url', 
        'description_ar', 
        'description_tr', 
        'category', 
        'stock'
    )
    
    class Media:
        js = ('admin/js/product_fetch.js',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'replied')
    list_filter = ('replied', 'created_at')

# REMOVED Settings from Admin (as requested)
# @admin.register(Setting)
# class SettingAdmin(admin.ModelAdmin):
#     list_display = ('site_name', 'whatsapp_number', 'language')

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'created_at', 'user_agent')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
