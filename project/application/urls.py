
from django.urls import path
from application import views
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('checkout/',views.checkout,name="checkout"),
	path('order-success/', views.order_success, name='order_success'),
	path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    
   
]