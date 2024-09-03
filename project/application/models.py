from django.db import models

class Product(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    quantity_sold = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Use DecimalField for prices
    image = models.ImageField(upload_to='images/images', default="")

    def __str__(self): 
        return self.item_name

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.JSONField()  # Store ordered items in JSON format
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Use DecimalField for amount
    name = models.CharField(max_length=90)
    email = models.EmailField(max_length=90)  # Use EmailField for validation
    address1 = models.CharField(max_length=200, default="N/A")
    address2 = models.CharField(max_length=200, default="N/A", blank=True)
    city = models.CharField(max_length=100, default="N/A")
    state = models.CharField(max_length=100, default="N/A")
    zip_code = models.CharField(max_length=20, default="N/A")  # Adjusted max_length for zip_code
    is_paid = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, default="N/A")  # Adjusted max_length for phone
    session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    update_desc = models.CharField(max_length=5000)
    delivered = models.BooleanField(default=False)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."