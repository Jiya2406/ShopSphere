from idlelib.debugobj import make_objecttreeitem
from tkinter.font import names

from click import password_option
from .models import *
from app1.models import Category
from django.shortcuts import render, redirect


# Create your views here.

def seller_index(request):
    cat_data = Category.objects.all()
    if 'login' in request.session and request.session["seller"]:
        return render(request, 'seller_index.html', {'category': cat_data, 'logged_in': True})
    else:
        return render(request, 'seller_index.html', {'category': cat_data})


def LogIn(request):
    if request.method == 'POST':
        try:
            register_data = SellerRegistration.objects.get(email = request.POST['email'])
            if request.POST['password'] == register_data.password:
                if register_data.accept:
                    request.session['login'] = register_data.email
                    request.session['seller'] = True
                    return redirect('seller_index')
                else:
                    return render(request, 'SellerLogIn.html', {'incorrect': "Seller request is pending..."})
            else:
                return render(request,'SellerLogIn.html',{'incorrect':"the pasword is incorrect.."})
        except:
            return render(request,'SellerLogIn.html',{'not_registred':"This email is not registerd.."})
    return render(request,'SellerLogIn.html')


def SignUp(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        password = request.POST["password"]
        mob = request.POST["mob"]
        address = request.POST["add"]

        try:
            already_registered = SellerRegistration.objects.get(email = email)
            if already_registered:
                return render(request,'SignUp.html',{'already_registerd':"This email is already registered.."})
        except:
            obj = SellerRegistration.objects.create(name=name, email=email, password=password, mob=mob, add=address)
            obj.save()
            return render(request,'SignUp.html',{'stored':"registration sucessfull.."})
    return render(request, "SignUp.html")


def LogOut(request):
    del request.session['login']
    del request.session['seller']
    return redirect('seller_index')