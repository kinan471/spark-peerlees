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
    created_at = models.DateTimeField(auto_now_add=True)
    akakce_url = models.TextField(null=True, blank=True)
    meta_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name_ar

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Setting(models.Model):
    id = models.CharField(primary_key=True, max_length=50, default='default')
    site_name = models.CharField(max_length=255, default='Spark Swarder - التنقل الكهربائي')
    tagline = models.TextField(null=True, blank=True, default='منصتك الأولى للدراجات والسكوترات الكهربائية')
    whatsapp_number = models.CharField(max_length=50, default='+905555555555')
    primary_color = models.CharField(max_length=50, default='#fbbf24')
    secondary_color = models.CharField(max_length=50, default='#10b981')
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='ar', choices=[('ar', 'Arabic'), ('tr', 'Turkish')])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name

class Visit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.TextField()
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.path} at {self.created_at}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='orders')
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_phone = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"
