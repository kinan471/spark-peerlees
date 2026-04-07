from django.db import models
import uuid

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ar = models.TextField()
    name_tr = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image_url = models.TextField()
    description_ar = models.TextField(null=True, blank=True)
    description_tr = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, default='ebike')
    stock = models.IntegerField(default=1)
    
    # Technical Specs
    power = models.CharField(max_length=50, null=True, blank=True, help_text="e.g. 1000W")
    range = models.CharField(max_length=50, null=True, blank=True, help_text="e.g. 50km")
    weight = models.CharField(max_length=50, null=True, blank=True, help_text="e.g. 25kg")
    speed = models.CharField(max_length=50, null=True, blank=True, help_text="e.g. 45km/h")
    is_spark_certified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    akakce_url = models.TextField(null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Show this product in the home page slider")
    meta_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name_ar

class BatteryCustomization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voltage = models.PositiveIntegerField(help_text="Voltage (V)")
    capacity = models.PositiveIntegerField(help_text="Capacity (Ah)")
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.voltage}V {self.capacity}Ah - {self.customer_name}"

class MaintenanceRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue_type = models.CharField(max_length=50, choices=[
        ('electrical', 'Electrical Fault (عطل كهربائي)'),
        ('mechanical', 'Mechanical Fault (عطل ميكانيكي)'),
        ('general', 'General Maintenance (صيانة عامة)'),
    ])
    description = models.TextField()
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_issue_type_display()} - {self.customer_name}"

class TradeInRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('ebike', 'E-bike (دراجة كهربائية)'),
        ('scooter', 'E-Scooter (سكوتر كهربائي)'),
    ])
    brand_model = models.CharField(max_length=255)
    condition = models.TextField()
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade-in {self.brand_model} - {self.customer_name}"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default="Swarder")
    tagline = models.TextField(default="Akıllı Hareketlilik Çözümleri")
    whatsapp_number = models.CharField(max_length=50, default="905387845388")
    contact_email = models.EmailField(default="info@swarder.com")
    contact_address = models.TextField(default="Istanbul, Turkey")
    maintenance_contact = models.CharField(max_length=50, default="905387845388")
    
    def __str__(self):
        return self.site_name

class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    customer_email = models.EmailField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class Visitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.TextField(default='/')
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.path} at {self.created_at}"

class HeroSlider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title_ar = models.CharField(max_length=255, null=True, blank=True)
    title_tr = models.CharField(max_length=255, null=True, blank=True)
    subtitle_ar = models.TextField(null=True, blank=True)
    subtitle_tr = models.TextField(null=True, blank=True)
    image_url = models.TextField()
    link_url = models.CharField(max_length=255, default='/store')
    button_text_ar = models.CharField(max_length=100, default='تسوق الآن')
    button_text_tr = models.CharField(max_length=100, default='Şimdi Al')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title_tr or str(self.id)
