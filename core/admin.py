from django.contrib import admin
from .models import (
    Product, BatteryCustomization, MaintenanceRequest, 
    TradeInRequest, SiteSettings, ContactMessage, 
    Order, Visitor, HeroSlider
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'price', 'category', 'stock', 'is_featured', 'is_spark_certified')
    search_fields = ('name_ar', 'name_tr')
    
    fields = (
        'akakce_url', 
        'is_featured',
        'name_ar', 
        'name_tr', 
        'price', 
        'image_url', 
        'description_ar', 
        'description_tr', 
        'category', 
        'stock',
        'power',
        'range',
        'weight',
        'speed',
        'is_spark_certified'
    )

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'whatsapp_number', 'contact_email')

@admin.register(BatteryCustomization)
class BatteryCustomizationAdmin(admin.ModelAdmin):
    list_display = ('voltage', 'capacity', 'customer_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('issue_type', 'customer_name', 'status', 'created_at')
    list_filter = ('issue_type', 'status', 'created_at')

@admin.register(TradeInRequest)
class TradeInRequestAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'brand_model', 'customer_name', 'status', 'created_at')
    list_filter = ('vehicle_type', 'status', 'created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_read', 'replied', 'created_at')
    list_filter = ('is_read', 'replied', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'path', 'created_at')
    list_filter = ('created_at',)

@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title_ar', 'title_tr')
