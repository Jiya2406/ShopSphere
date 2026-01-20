from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import *
import random
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO

# Try to import PDF functionality, make it optional
try:
    from xhtml2pdf import pisa # type: ignore
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Create your views here.


def demo(request):
    return  HttpResponse("this is my first view...")

def first(request):
    return render(request,'first.html')

def table(request):
    cat_data = Category.objects.all()
    print(cat_data)
    # a = ["hello" , "tegyh", 7545 , True]
    # for i in a:
    #     print(i)
    # for i in cat_data:
    #     print(i.id)
    #     print(i.name)
    #     print(i.image)
    return render(request,'table.html',{'category':cat_data})


def store_student(request):
    if request.method == 'POST' and request.FILES:
        store_student = Category()
        store_student.name = request.POST['uname']
        store_student.image = request.FILES['img']
        store_student.save()
    return render(request,'student.html')


def register(request):
    if request.method == 'POST':
        store_reg = Registration()
        store_reg.name = request.POST['name']
        store_reg.email = request.POST['email']
        store_reg.add = request.POST['add']
        store_reg.mob = request.POST['mob']
        store_reg.password = request.POST['password']
        try:
            already_registered = Registration.objects.get(email = request.POST['email'])
            if already_registered:
                return render(request,'register.html',{'already_registerd':"This email is already registered.."})
        except:
            store_reg.save()
            # Set session after successful registration
            request.session['login'] = store_reg.email
            return redirect('index')
    else:
        return render(request,'register.html')


def login(request):
    if request.method == 'POST':
        try:
            register_data = Registration.objects.get(email = request.POST['email'])
            if request.POST['password'] == register_data.password:
                request.session['login'] = register_data.email
                return redirect('index')
            else:
                return render(request,'login.html',{'incorrect':"the pasword is incorrect.."})
        except:
            return render(request,'login.html',{'not_registred':"This email is not registerd.."})
    return render(request,'login.html')

def index(request):
    cat_data = Category.objects.all()
    context = {'category': cat_data}
    if 'login' in request.session:   
        context['logged_in'] = True
    return render(request,'index.html', context)


def logout(request):
    del request.session['login']
    return redirect('index')


# def cat_pro(request,id):
#     prod = Product.objects.filter(category = id)
#     if 'login' in request.session:  
#         return render(request,'cat_pro.html',{'prod':prod,'logged_in':True})
#     else:
#         return render(request,'cat_pro.html',{'prod':prod})



def product_detail(request,id):
    single_product = get_object_or_404(Product,id = id)
    context = {'product': single_product}
    
    # Check if user is logged in
    if 'login' in request.session:  
        context['logged_in'] = True
        logged_in = Registration.objects.get(email = request.session['login'])
        
        if request.method == "POST" and ('buy' in request.POST or 'wish' in request.POST or 'cart' in request.POST):
            if 'buy' in request.POST:
                add_to_cart = Cart()
                add_to_cart.pro = single_product
                add_to_cart.user = logged_in
                add_to_cart.qty = request.POST['qty']
                add_to_cart.total_amount = int(request.POST['qty']) * single_product.price
                add_to_cart.save()
                single_product.stock -= int(request.POST['qty'])
                single_product.save()
                request.session['proid'] = id
                request.session['qty'] = request.POST['qty']
                request.session['amount'] = int(request.POST['qty']) * single_product.price
                return redirect('checkout')
            elif 'wish' in request.POST:
                add_to_wishlist = Wishlist()
                add_to_wishlist.pro = single_product
                add_to_wishlist.user = logged_in
                add_to_wishlist.save()
                return redirect('wish')
            elif 'cart' in request.POST:
                request.session['proid'] = id
                request.session['qty'] = request.POST['qty']
                add_to_cart = Cart()
                add_to_cart.pro = single_product
                add_to_cart.user = logged_in
                add_to_cart.qty = request.POST['qty']
                add_to_cart.total_amount = int(request.POST['qty']) * single_product.price
                add_to_cart.save()
                single_product.stock -= int(request.POST['qty'])
                single_product.save()
                return redirect('cart_view')
    
    return render(request,'product.html', context)


def checkout(request):
    if 'login' in request.session:
        logged_in_user = Registration.objects.get(email = request.session['login'])
        tempCart = Cart.objects.filter(ordered=False, user__email = request.session['login'])
        if request.method == 'POST':
            if request.POST['paymentvia'] == 'cod':
                c = request.POST['city']
                s = request.POST['state']
                p = request.POST['pin']
                if s and c and p:
                    total_amount = 0
                    for item in tempCart:
                        item_total = item.qty * item.pro.price
                        total_amount += item_total
                    store_order = Order.objects.create(
                        total_amount = total_amount,
                        user=logged_in_user,
                        payment_mode=request.POST['paymentvia'],
                        transaction_id=str(random.randint(10**9, 10**10 - 1)),
                        add=request.POST['add'],
                        mob=request.POST['mob'],
                        city=request.POST['city'],
                        state=request.POST['state'],
                        pin_code=request.POST['pin'],
                        ordered = True
                    )
                    store_order.prods.add(*tempCart)
                    tempCart.update(ordered=True)
                    store_order.save()
                    # Decrease stock for all ordered items
                    for cart_item in tempCart:
                        product = cart_item.pro
                        product.stock = max(0, product.stock - cart_item.qty)
                        product.save()
                    order = get_object_or_404(Order, id=store_order.id)
                    param = {'order': order}
                    return render(request, 'order.html', param)
                else:
                    return HttpResponse("<script>alert('Add City, State, Zip Code');window.location.href='/checkout/';</script>")
            else:
                c = request.POST['city']
                s = request.POST['state']
                p = request.POST['pin']
                if s and c and p:
                    total_amount = 0
                    for item in tempCart:
                        item_total = item.qty * item.pro.price
                        total_amount += item_total
                    request.session['total_amount'] = total_amount
                    request.session['add'] = request.POST['add']
                    request.session['mob'] = request.POST['mob']
                    request.session['pin'] = request.POST['pin']
                    request.session['city'] = request.POST['city']
                    request.session['state'] = request.POST['state']
                    return render(request, 'checkout.html', {'logged_in': logged_in_user, 'error': 'Online payment is currently disabled. Please use Cash on Delivery.'})

                else:
                    return HttpResponse("<script>alert('Add City, State, Zip Code');window.location.href='/checkout/';</script>")
        else:
            # Build context for displaying cart items and totals on checkout page
            cart_items = Cart.objects.filter(ordered=False, user=logged_in_user)
            prolist = []
            total_amount = 0
            for item in cart_items:
                prolist.append({
                    'proname': item.pro.name,
                    'prodis': item.pro.description,
                    'proprice': item.pro.price,
                    'proimg': item.pro.image,
                    'qty': item.qty,
                })
                total_amount += item.qty * item.pro.price

            context = {
                'logged_in': logged_in_user,
                'prolist': prolist,
                'total': total_amount,
                'cart_count': cart_items.count(),
            }
            return render(request,'checkout.html', context)
    else:
        return redirect('login')
    
def products_by_category(request, name):
    category = get_object_or_404(Category, name=name)
    products = Product.objects.filter(category=category)
    context = {'products': products, 'category': category}
    if 'login' in request.session:
        context['logged_in'] = True
    return render(request, 'category_products.html', context)

# def product_list_by_category(request, id):
#     cat = Category.objects.get(id=id)
#     prod = Product.objects.filter(category=cat)
#     context = {'products': prod, 'category': cat}
#     if 'login' in request.session:
#         context['logged_in'] = True
#     return render(request, 'product.html', context)

# def category_products(request, id):
#     cat = Category.objects.get(id=id)
#     products = Product.objects.filter(category=cat)
#     context = {'products': products, 'category': cat}
#     if 'login' in request.session:
#         context['logged_in'] = True
#     return render(request, 'product.html', context)

# def view_products_by_category(request, id):
#     products = Product.objects.filter(category=id)
#     return render(request, 'product_list.html', {'products': products})

from .models import Category, Product

# def category_products(request, category_id):
#     category = Category.objects.get(id=category_id)
#     products = Product.objects.filter(category=category)
#     context = {
#         'category': category,
#         'products': products,
#         'logged_in': 'login' in request.session
#     }
#     return render(request, 'category_products.html', context)


       
# import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt 


# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))


# def razorpayment(request):
#     amount = request.session['total_amount'] * 100
#     currency = 'INR'
#     razorpay_order = razorpay_client.order.create(dict(amount = amount,currency = currency,payment_capture = '0'))
#     return render(request,'razorpay.html',{'razorpay_merchant_key':settings.RAZORPAY_KEY_ID,
#                                           'razorpay_amount':amount,
#                                           'currency':currency,
#                                            'razorpay_order_id': razorpay_order['id'],
#                                            'callback_url':'http://127.0.0.1:8000/payment_handler/'})

# @csrf_exempt
# def payment_handler(request):
#     if request.method == 'POST':
#        try:
#            payment_id = request.POST.get('razorpay_payment_id', ' ')
#            order_id = request.POST.get('razorpay_order_id', ' ')
#            signature = request.POST.get('razorpay_signature', ' ')
#            param_dict = {
#                'razorpay_payment_id':payment_id,
#                'razorpay_order_id': order_id,
#                'razorpay_signature' : signature
#             }
#             razorpay_client.utility.verify_payment_signature(param_dict)
#             amount = request.session['total_amount'] * 100
#             razorpay_client.payment.capture(payment_id,amount)
#             pro = Product.objects.get(id = request.session['proid'])
#             logged_in_user = Registration.objects.get(email = request.session['login'])

#             tempCart = Cart.objects.filter(ordered=False, user__email=request.session['login'])

#            order_store = Order.objects.create(
#                user = logged_in_user,
#                payment_mode = "online",
#                transaction_id = payment_id,
#                total_amount = request.session['total_amount'],
#                 add =  request.session['add'],
#                 mob = request.session['mob'],
#                 city = request.session['city'],
#                 state = request.session['state'],
#                 pin_code = request.session['pin'],
#                 ordered=True
#            )
#             order_store.prods.add(*tempCart)
#             tempCart.update(ordered=True)
#             order_store.save()
#             pro.stock -= int(request.session['qty'])
#             pro.save()
#             order = get_object_or_404(Order, id=order_store.id)
#             param = {'order': order}
#             return render(request, 'order.html', param)
#         except Exception as e:
#            print(e,"errrrrooorrrrrr")
#            return HttpResponseBadRequest()
#     else:
#        return HttpResponseBadRequest()


def wish(request):
    if 'login' in request.session:
        logged_in_user = Registration.objects.get(email = request.session['login'])        
        wishlist_data = Wishlist.objects.filter(user = logged_in_user)
        total = 0
        for i in wishlist_data:
            total += i.pro.price 
        return render(request,'wish.html',{'logged_in':True,"wishlist":wishlist_data,'total':total})
    else:
        return redirect('login')

def remove_wishlist(request, pid):
    if 'login' in request.session:
        logged_in_user = Registration.objects.get(email=request.session['login'])
        Wishlist.objects.filter(user=logged_in_user, pro_id=pid).delete()
        return redirect('wish')
    else:
        return redirect('login')  

def remove_all_wishlist(request):
    if 'login' in request.session:
        user = Registration.objects.get(email=request.session['login'])
        Wishlist.objects.filter(user=user).delete()
        return redirect('wish')
    else:
        return redirect('login')
  

def cart_view(request):
    if 'login' in request.session:
        logged_in_user = Registration.objects.get(email = request.session['login'])        
        cart_data = Cart.objects.filter(user = logged_in_user, ordered=False)
        total = 0
        for i in cart_data:
            total += i.total_amount
        if cart_data:
            if 'outofstock' in request.session:
                del request.session['outofstock']
                return render(request,'cart.html',{'cart_data':cart_data,'logged_in':True,'total':total,'outofstock':"this product is out of stock."})
            else:
                return render(request,'cart.html',{'cart_data':cart_data,'logged_in':True,'total':total})
        else:
                return render(request,'cart.html',{'logged_in':True})
    else:
        return redirect('login')
    

def add_qty(request,id):
    if 'login' in request.session:
        cart_row = Cart.objects.get(id = id)
        pro = Product.objects.get(id = cart_row.pro.id)
        if pro.stock <= 0:
            request.session['outofstock'] = True
            return redirect('cart_view')
        else:
            cart_row.qty += 1
            cart_row.total_amount += pro.price
            cart_row.save()
            pro.stock -= 1
            pro.save()
            return redirect('cart_view')
    else:
        return redirect('login')

def minus_qty(request,id):
    if 'login' in request.session:
        cart_data = Cart.objects.get(id = id)
        pro = Product.objects.get(id = cart_data.pro.id)
        if cart_data.qty <= 1:
            cart_data.delete()
            return redirect('cart_view')
        else:
            cart_data.qty -= 1
            cart_data.total_amount -= pro.price
            cart_data.save()
            pro.stock += 1
            pro.save()
            return redirect('cart_view')
    else:
        return redirect('login')
    
def remove(request,id):
    if 'login' in request.session:
        cart_data = Cart.objects.get(id = id)
        pro = Product.objects.get(id = cart_data.pro.id)
        pro.stock += cart_data.qty
        pro.save()
        cart_data.delete()
        return redirect('cart_view')
    else:
        return redirect('login')


def remove_all(request):
    if 'login' in request.session:
        user = Registration.objects.get(email = request.session['login'])
        cart_data = Cart.objects.filter(user = user)
        for i in cart_data:
            pro = Product.objects.get(id = i.pro.id)
            pro.stock += i.qty
            pro.save()
            i.delete()
        return redirect('cart_view')
    else:
        return redirect('login')


def all_orders(request):
    if 'login' in request.session:
        orders = Order.objects.filter(ordered=True, user__email=request.session['login']).order_by('-id')
        return render(request, "orderhistory.html", {'orders':orders, 'logged_in':True})
    else:
        return redirect('login')

def single_invoice(request):
    if 'login' in request.session:
        id = request.GET['id']
        order = get_object_or_404(Order, id=id)
        param = {'order': order}
        return render(request, "order.html", param)
    else:
        return redirect('login')

def download_invoice_pdf(request):
    if not PDF_AVAILABLE:
        return HttpResponse("PDF generation is not available. Please install xhtml2pdf package.", status=400)
    
    if 'login' in request.session:
        id = request.GET['id']
        order = get_object_or_404(Order, id=id)
        
        # Render the PDF template
        template = get_template('order.html')
        context = {'order': order}
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.CreatePDF(html, result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.transaction_id}.pdf"'
            return response
    
    return redirect('login')




def search_products(request):
    query = request.GET.get('q', '')
    products = []
    if query:
        products = Product.objects.filter(name__icontains=query)
    
    context = {
        'products': products,
        'query': query,
        'logged_in': 'login' in request.session
    }
    return render(request, 'search_results.html', context)

def contact(request):
    context = {}
    if 'login' in request.session:
        context['logged_in'] = True
    return render(request, 'contact.html', context)


def wishlist_checkout(request):
    if 'login' in request.session:
        logged_in_user = Registration.objects.get(email=request.session['login'])
        wishlist_items = Wishlist.objects.filter(user=logged_in_user)
        if not wishlist_items.exists():
            return redirect('wish')
        # Ensure each wishlist product has a temporary cart entry for checkout
        for w in wishlist_items:
            cart_entry, created = Cart.objects.get_or_create(
                user=logged_in_user,
                pro=w.pro,
                ordered=False,
                defaults={'qty': 1, 'total_amount': w.pro.price}
            )
            if not created:
                # If already present, ensure at least qty 1 and amount consistent
                if cart_entry.qty <= 0:
                    cart_entry.qty = 1
                cart_entry.total_amount = cart_entry.qty * cart_entry.pro.price
                cart_entry.save()
        return redirect('checkout')
    else:
        return redirect('login')
