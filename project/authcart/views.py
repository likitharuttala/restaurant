from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import generate_token
from django.utils.encoding import force_bytes, force_str  # Use force_str instead of force_text for Django 4.0+
from django.core.mail.message import EmailMessage
from django.core.mail import send_mail
from django.core import mail
from django.conf import settings
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        if password != confirm_password:
            messages.warning(request, "Password is Not Matching")
            return render(request, 'signup.html')

        try:
            if User.objects.get(username=email):
                messages.info(request, "Email is taken")
                return render(request, 'signup.html')
                # return HttpResponse("Email already exists")
        except User.DoesNotExist:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = False
            user.save()
            email_subject = "Activate Your Account"
            message = render_to_string('activate.html', {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
            email_message.send()
            messages.success(request, "ACTIVATE YOUR ACCOUNT BY CLICKING THE LINK")
            return redirect('/auth/login/')

        return HttpResponse("User created: " + email)

    return render(request, "signup.html")

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # Use force_str instead of force_text
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, "Account Activated Successfully")
            return redirect('/auth/login/')
        else:
            return render(request, 'activatefail.html')


def handlelogin(request):
    if request.method=="POST":
        username=request.POST['email']
        userpassword=request.POST['pass1'] 
        myuser=authenticate(username=username, password=userpassword)
        if myuser is not None:
            login(request, myuser)
            messages.success (request, "Login Success")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials") 
            return redirect('/auth/login')


    return render(request,'login.html')



def handlelogout(request):
    logout(request)
    messages.info(request,"logout success")
    return redirect('/auth/login')
