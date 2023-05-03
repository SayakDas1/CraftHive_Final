from django.shortcuts import render, redirect
from auction.models import AuctionProduct
from auction.models import User
import time
import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.conf import settings
from instamojo_wrapper import Instamojo

KEY = settings.HASH_KEY
hasher = 'pbkdf2_sha1'

api = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/');


def auction(request):
    products = AuctionProduct.objects.all()
    for val in products:
        print(val)
        end_time = val.start_time + datetime.timedelta(hours = val.duration_hours, minutes=val.duration_mins)
        print(val.start_time)
        print(end_time)
        val.end_time = end_time
        end_naive = val.end_time.replace(tzinfo=None)
        curr_time = datetime.datetime.now()
        val.save()
    context = {'products' : AuctionProduct.objects.all()}
    print(context)
    return render(request, 'auction.html', context)

def auc_product(request, myid):
    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        print("Bid was raised by ", useremail)
        raise_amt = int(request.POST.get('bid_amt'))
        graph = request.POST.get('graph')
        print("Graph ",graph)
        product = get_object_or_404(AuctionProduct, id=myid)
        end_time = product.end_time

        if timezone.now() < end_time:
            with transaction.atomic():
                product.refresh_from_db()
                if raise_amt > product.prod_price:
                    product.prod_price = raise_amt
                    if(product.second_email != product.winner_email):
                        product.second_email = product.winner_email
                    product.winner_email = useremail
                    product.graph = graph
                    product.save()
                else:
                    return render(request, 'auc_product.html', {'product': product, 'bid': 'fail'})
        else:
            return render(request, 'auc_product.html', {'product': product, 'bid': 'tle'})

    product = get_object_or_404(AuctionProduct, id=myid)
    return render(request, 'auc_product.html', {'product': product, 'bid': 'success'})


def register(request):
    if(request.method == 'POST'):
        print('got user registration')
        username = request.POST.get('name')
        useremail = request.POST.get('email')
        userpass = request.POST.get('password')
        #print(datetime.datetime.now().time())
        user_check = User.objects.filter(user_email = useremail)
        if(len(user_check)>0):
                print("Error , duplicate email")
                return render(request, 'register.html', {'login' : 'fail', 'reason' : 'This email id is already registered with us'})
        password = make_password(userpass, KEY, hasher)
        user = User(user_name = username, user_email = useremail, password = password)
        user.save()
        return auction(request)

    return render(request, 'register.html')


def contact(request):
    return render(request,'contact.html')


def login(request):
    print("login page def")
    if(request.method == 'POST'):
        print("Got login request")
        useremail = request.POST.get('email')
        userpass = request.POST.get('password')
        print(useremail, userpass)
        password = make_password(userpass, KEY, hasher)
        user = User.objects.filter(user_email = useremail, password = password)
        print("Print this line")
        if(len(user)>0):
                print("MAtch o hoe gache , returning render")
                return auction(request)
        else:
            return render(request, 'login.html', {'login' : 'fail', 'reason' : 'incorrect email or password'})
        
            

    return render(request, 'login.html')


def winner(request):
    products = AuctionProduct.objects.all()
    curr_time = timezone.now()

    later = curr_time + datetime.timedelta(hours=5, minutes=30)
    curr_time = later

    filtered_products = []

    for product in products:
        end_time = product.end_time
        print('current time : ----',curr_time)
        print('end time : ----',end_time)
        if curr_time > end_time + timezone.timedelta(hours=1):
            product.winner_email = product.second_email
            product.save()
            print('winner email changed')

        if curr_time > end_time + timezone.timedelta(hours=2):
            product.winner_email = 'default@gmail.com'
            product.save()

        if curr_time > end_time:
            filtered_products.append(product)

    context = {'closed_products' : filtered_products}
    return render(request, 'winner.html', context)

def payment(request, id, email):
    product = AuctionProduct.objects.get(id=id)
    print(product, email)
    try:
        response = api.payment_request_create(
            amount=product.prod_price,
            purpose=product.prod_name,
            send_email=True,
            buyer_name=User.objects.get(user_email=email).user_name,
            email=email,
            redirect_url="http://127.0.0.1:8000/auction/order-status/"+str(id)
        )
        print(response)
        return render(request, 'payment.html', context={'payment_url': response['payment_request']['longurl']})
    
    except Exception as e:
        return HttpResponse(e)

def orderStatus(request, id):
    if request.method=="GET":
        payment_id = request.GET.get('payment_id')
        payment_request_id = request.GET.get('payment_request_id')

        response = api.payment_request_status(payment_request_id)
        response2 = api.payment_request_payment_status(payment_request_id, payment_id)

        res1=response['payment_request']['status']
        res2=response2['payment_request']['payment']['status']

        prod = AuctionProduct.objects.get(id=id)
        
        if(res1=='Completed'):
            return render(request,'status.html',{'success':1,'prod':prod})
        elif(res1=='Sent' and res2=='Failed'):
            return render(request,'status.html',{'success':0})

def prod_upload(request):
    if request.method=='POST':
        name=request.POST.get('name')
        desc=request.POST.get('desc')
        seller=request.POST.get('seller')
        artist=request.POST.get('artist')

        image=request.FILES['prod_img']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        start_price=request.POST.get('start_price')
        start_date=request.POST.get('start_date')
        start_time=request.POST.get('start_time')
        hours=request.POST.get('hours')
        mins=request.POST.get('mins')

        product=AuctionProduct(prod_name=name, prod_desc = desc, seller = seller, artist=artist, prod_start_price=int(start_price), prod_price = int(start_price), start_time=start_date + " " + start_time, end_time=start_date + " " + start_time,duration_hours = hours, duration_mins = mins, winner_email = "default@gmail.com", prod_image = image)
        product.save()
        return redirect('/auction')
        
    return render(request,'upload_prod.html')

def live(request,id):
        print('Request')
        product = AuctionProduct.objects.get(id=id)
        #return render(request, "live.html", {"graph": json.dumps(product.graph), "id":json.dumps(product.id)})
        return render(request,'live.html',{'product':product})