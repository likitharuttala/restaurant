from django.contrib import admin
from application.models import Product,Orders,OrderUpdate

# Register your models here.
admin.site.register(Product)
admin.site.register(Orders)
admin.site.register(OrderUpdate)