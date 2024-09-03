from django.shortcuts import render, redirect
from application.models import Product, Orders
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
import json
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Orders

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'item_id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + (n % 4 > 0)
        allProds.append([prod, range(1, nSlides + 1), nSlides])
    params = {'allProds': allProds}
    return render(request, "index.html", params)

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        amount = request.POST.get('amt', '')  # Fetch the total amount from the form

        # Save order
        order = Orders(
            items_json=items_json,
            name=name,
            amount=amount,  # Store the amount directly as INR
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        order.save()

        # Print the amount from the database
        print(f"Amount from database (INR): {order.amount}")

        try:
            YOUR_DOMAIN = "http://127.0.0.1:8000"  # Or your production domain

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': 'Order #' + str(order.order_id),
                            },
                            'unit_amount': int(order.amount) * 100,  # Convert INR to paise
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f'{YOUR_DOMAIN}/order-success/?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{YOUR_DOMAIN}/checkout/',
            )

            # Update the order with the session_id
            order.session_id = checkout_session.id
            order.save()

            return redirect(checkout_session.url, code=303)
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {e.user_message}")
            return redirect('/checkout')

    return render(request, 'checkout.html')

import json
from django.http import HttpResponse
from django.shortcuts import render
from .models import Orders

def order_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            # Fetch the order using the session ID
            order = Orders.objects.get(session_id=session_id)
            print("Order found:", order)
            print("Order items JSON:", order.items_json)
            
            # Deserialize items_json to a dictionary
            items_dict = json.loads(order.items_json)
            
            # Convert items_dict to a list of dictionaries with clearer structure
            items_list = []
            for key, value in items_dict.items():
                item = {
                    'id': key,
                    'quantity': value[0],
                    'name': value[1],
                    'price': value[2]
                }
                items_list.append(item)
            
            context = {
                'order': order,
                'order_id': order.order_id,
                'items_list': items_list,  # Pass the list of dictionaries to the template
                'address1': order.address1,
                'address2': order.address2,
                'city': order.city,
                'state': order.state,
                'zip_code': order.zip_code,
                'phone': order.phone,
                'email': order.email
            }
            return render(request, 'order_success.html', context)
        except Orders.DoesNotExist:
            return HttpResponse("Order does not exist.", status=404)
        except json.JSONDecodeError:
            return HttpResponse("Error decoding JSON data.", status=500)
    else:
        return HttpResponse("Invalid session ID.", status=400)



@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        try:
            total_amount = request.POST.get('amt', 0)
            total_amount = float(total_amount)
            unit_amount = int(total_amount * 100)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': 'Food order',
                            },
                            'unit_amount': unit_amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url='http://127.0.0.1:8000/order-success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://127.0.0.1:8000/checkout/',
            )

            # Save the order with the session ID
            order = Orders(
                items_json=request.POST.get('itemsJson'),
                name=request.POST.get('name'),
                amount=total_amount,
                email=request.POST.get('email'),
                address1=request.POST.get('address1'),
                address2=request.POST.get('address2'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip_code=request.POST.get('zip_code'),
                phone=request.POST.get('phone'),
                session_id=checkout_session.id  # Save the session ID
            )
            order.save()

            return JsonResponse({'id': checkout_session.id})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)




def handlelogin(request):
    if request.method == 'POST':
        loginusername = request.POST['email']
        loginpassword = request.POST['pass1']
        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request, user)
            messages.info(request, "Successfully Logged In")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/login')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 != pass2:
            messages.error(request, "Passwords do not match, please try again!")
            return redirect('/signup')
        try:
            if User.objects.get(username=email):
                messages.warning(request, "Email already exists")
                return redirect('/signup')
        except User.DoesNotExist:
            pass 

        user = User.objects.create_user(username=email, email=email, password=pass1)
        user.save()
        messages.info(request, 'Thanks for signing up')
        return redirect('/login')

    return render(request, "signup.html")        

def logouts(request):
    logout(request)
    messages.warning(request, "Logout successful")
    return render(request, 'login.html')
