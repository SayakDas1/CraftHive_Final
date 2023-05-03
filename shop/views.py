from django.shortcuts import render,redirect
from .models import Product, Contact, Orders, OrderUpdate, Review
from math import ceil
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login, get_user_model
from instamojo_wrapper import Instamojo
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

User = get_user_model()

api = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/');

#Create your views here
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query.lower(), item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request, 'shop/about.html')

@login_required(login_url='/login')
def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    productreview = Product.objects.get(id=myid)
    review = Review.objects.filter(product=productreview)

    no=0
    tr=0
    for i in review.iterator():
        no = no + 1
        tr = tr + i.rate

    if(no!=0):
        rate = round(tr / no)
    else:
        rate=0

    return render(request, 'shop/prodView.html', {'product':product[0],'reviews':review,'n':range(rate),'r':range(5-rate),'no':no,'avg':rate,'error':0})

@login_required(login_url='/login')
def checkout(request):
    if request.method=="POST":
        total = request.POST.get('totalPrice','')
        name = request.user.username
        email = request.user.email

        try:
            response = api.payment_request_create(
                amount=total,
                purpose="Your Products",
                send_email=True,
                buyer_name=name,
                email=email,
                #needs to be changed on hosting
                redirect_url="http://127.0.0.1:8000/order-status/"
            )
            print(response)
            return render(request, 'shop/order.html', context={'payment_url': response['payment_request']['longurl']})
    
        except Exception as e:
            return HttpResponse(e)
    
    return render(request, 'shop/checkout.html')

def loginUser(request):
     if request.method=="POST":
        username = request.POST.get('name')
        password = request.POST.get('pwd')
        #check authentication details
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return index(request)
        else:
            return render(request, 'shop/login.html',{'problem':'1'})
        
     return render(request, 'shop/login.html')

def logoutUser(request):
    logout(request)
    return redirect("/")

def register(request):
    if request.method=="POST":
        username = request.POST.get('username')
        pwd1 = request.POST.get('pwd1')
        email = request.POST.get('email')
        role = request.POST.get('role')
        if role=='':
            role='2'
        check = User.objects.filter(email=email)
        if(len(check)==0):
            user = User.objects.create_user(username, email, pwd1)
            if role=='2':
                user.is_customer = 1
            elif role=='3':
                user.is_seller = 1

            user.save()
            user = authenticate(username=username, password=pwd1)
            login(request, user)
            return index(request)
        else:
            return render(request,'shop/register.html',{'error':1})
        
    return render(request, 'shop/register.html')

def orderStatus(request):
    if request.method=="GET":
        payment_id = request.GET.get('payment_id')
        payment_request_id = request.GET.get('payment_request_id')

        response = api.payment_request_status(payment_request_id)
        response2 = api.payment_request_payment_status(payment_request_id, payment_id)

        res1=response['payment_request']['status']
        res2=response2['payment_request']['payment']['status']
        
        #print(res1,res2)

        if(res1=='Completed'):
            return redirect('success')
        elif(res1=='Sent' and res2=='Failed'):
            return redirect('failure')

def success(request):
    if request.method == 'POST':
        orderstr = request.POST.get('order')
        print("Success ",orderstr," ||| ", type(orderstr))
        #print(type(orderstr))
        order = json.loads(orderstr)

        #check For same order on refresh!
        orderchk = Orders.objects.filter(items_json=order.get('itemsJson'), name=request.user.username, email=request.user.email, address=order.get('address1')+" "+order.get('address2'), city=order.get('city'), state=order.get('state'), zip_code=order.get('zip'), phone=order.get('phone'), amount = order.get('totalPrice'))

        #print(orderchk[0].items_json," /TEST/ ",orderchk[0].order_id," /TEST/ ",len(orderchk))

        if(len(orderchk)==0):
            #Storing Order details in database
            orderdb = Orders(items_json=order.get('itemsJson'), name=request.user.username, email=request.user.email, address=order.get('address1')+" "+order.get('address2'), city=order.get('city'), state=order.get('state'), zip_code=order.get('zip'), phone=order.get('phone'), amount = order.get('totalPrice'))
            orderdb.save()
            update = OrderUpdate(order_id=orderdb.order_id, update_desc="The order has been placed")
            update.save()

            id = orderdb.order_id

            #Dynamic Stock Updation and sending email to sellerbased on items ordered
            data = json.loads(orderdb.items_json)
            print(data)
            for i in data:
                product = Product.objects.get(product_name = data.get(i)[1])
                send_mail( 
                            'Order has been placed for your product!', 
                            f'Hello {product.seller_name}, \nOrder has been placed for {data.get(i)[0]} x {product.product_name}. \nPlease make sure to process and ship the order as soon as possible. \n\nHappy Selling! \n\nRegards, \nCraftHive', 
                            settings.EMAIL_HOST_USER, 
                            [product.seller_email],
                            fail_silently=True,
                        )
                product.stock = product.stock - data.get(i)[0]
                product.save()

            #mail to customer
            send_mail( 
                'Your Order has been successfully placed!', 
                f'Hello {request.user.username}, \nOrder has been placed for your products on CraftHive! \nYour order will be shipped soon! \n\nThank You for Shopping with us! \n\nRegards, \nCraftHive', 
                settings.EMAIL_HOST_USER, 
                [request.user.email],
                fail_silently=True,
            )
                
            return render(request,'shop/payresult.html',{'order':orderdb,'success':True,'id':id})
        else:
            #print(orderchk[0]," /TEST/ ",orderchk[0].order_id)
            return render(request,'shop/payresult.html',{'order':orderchk[0],'success':True,'id':orderchk[0].order_id})
    return render(request,'shop/payresult.html',{'success':True})

def failure(request):
    return render(request,'shop/payresult.html',{'success':False})

def productReg(request):
    if request.method=='POST':
        name=request.POST.get('name')
        cat=request.POST.get('category')
        desc=request.POST.get('description')
        price=request.POST.get('price')

        image=request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        sname=request.user.username
        mail=request.user.email
        link=request.POST.get('link')
        stock=request.POST.get('stock')

        product=Product(product_name=name, category=cat, desc=desc, price=price, image=image, seller_name=sname, link=link, stock=stock,seller_email=mail)
        product.save()
        return redirect('/')
        
    return render(request,'shop/productreg.html')

def seller(request):
    if request.method=="POST":
        number=request.POST.get('stocks')
        idstr = request.POST.get('prodid')
        prods = Product.objects.get(id=idstr)
        prods.stock = number;
        prods.save();

    product = Product.objects.filter(seller_email=request.user.email)
    params = {'products':product}
    return render(request, 'shop/seller.html',params)

def category(request,cat):
    product = Product.objects.filter(category=cat)
    return render(request,'shop/category.html',{'product':product})
    
def review(request):
    if request.method=='GET':
        prod_id = request.GET.get('prod_id')
        product = Product.objects.get(id=prod_id)
        comment = request.GET.get('comment')
        rate = request.GET.get('rate')
        user = request.user
        review = Review.objects.filter(user=user, product=product)
        if(len(review)==0):
            Review(user=user,product=product,comment=comment,rate=rate).save()
        else:
                product = Product.objects.filter(id=prod_id)
                productreview = Product.objects.get(id=prod_id)
                review = Review.objects.filter(product=productreview)

                no=0
                tr=0
                for i in review.iterator():
                    no = no + 1
                    tr = tr + i.rate

                if(no!=0):
                    rate = round(tr / no)
                else:
                    rate=0

                return render(request, 'shop/prodView.html', {'product':product[0],'reviews':review,'n':range(rate),'r':range(5-rate),'no':no,'avg':rate,'error':1})

        return productView(request, prod_id)