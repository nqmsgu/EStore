from django.shortcuts import render,redirect,reverse
from app_store.models import *
from django.core.paginator import *
from app_cart.cart import *
from app_cart.models import *
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings
import feedparser
from django.http import JsonResponse
from rest_framework import viewsets,permissions
from app_store.serializers import ProductSerializer
from app_cart.views import them_vao_gio_hang
from urllib.parse import urlencode


def lien_he(request):
    cart=Cart(request)

    chuoi_kq=''
    if request.POST.get('btnLienHe'):
        name=request.POST.get('name')
        email=request.POST.get('email')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        phone=request.POST.get('phone')

        lien_he=Contact(
            name=name,
            email=email,
            phone_number=phone,
            subject=subject,
            message=message
        )
        lien_he.save()

        sender=settings.EMAIL_HOST_USER
        content='Chúng tôi đã nhận được thông tin của bạn, chúng tôi sẽ liên hệ với bạn sớm !!!'
        receivers=[email,sender]

        # ko định dạng html
        #send_mail(subject,content,sender,receivers)

        # định dạng html
        content1=f'<p><b>Chúng tôi sẽ liên hệ với bạn sớm !!!</b></p>'
        msg=EmailMultiAlternatives(subject,content1,sender,receivers)
        msg.attach_alternative(content1,'text/html')
        msg.send()

        chuoi_kq='''
            <div class="alert alert-success" role="alert">
                Gửi thông tin thành công !!!
            </div>
        '''

    return render(request, 'contact.html',{
        'cart_len':len(cart),
        'chuoi_kq':chuoi_kq,
    })


def trang_chu(request):
    cart=Cart(request)
    sliders = Slider.objects.all()
    brands = Brand.objects.all()
    subcategories_tbgd = SubCategory.objects.filter(category=1).values('id')
    list_id_subcategories_tbgd = [item['id']
                                  for item in list(subcategories_tbgd)]
    products_tbgd = Product.objects.filter(
        subcategory__in=list_id_subcategories_tbgd).order_by('-public_day')[:20]
    subcategories_ddnb = SubCategory.objects.filter(category=2).values('id')
    list_id_subcategories_ddnb = [item['id']
                                  for item in list(subcategories_ddnb)]
    products_ddnb = Product.objects.filter(
        subcategory__in=list_id_subcategories_ddnb).order_by('-public_day')[:20]
    return render(request, 'index.html', {
        'sliders': sliders,
        'brands': brands,
        'products_tbgd': products_tbgd,
        'products_ddnb': products_ddnb,
        'cart_len':len(cart),
    })


def danh_muc(request, id_subcategory):
    cart=Cart(request)
    subcategories = SubCategory.objects.order_by('name')
    if id_subcategory == 0:
        products = Product.objects.order_by('-public_day')
        subcategory_name=f'All products ({products.count()})'
    else:
        products = Product.objects.filter(
            subcategory=id_subcategory).order_by('-public_day')
        subcategory=SubCategory.objects.get(pk=id_subcategory)
        subcategory_name=f'{subcategory.name} ({products.count()})'
        
    price=''
    keyword=''
    if request.GET.get('gia'):
        keyword=request.GET.get('tukhoa').strip()
        price=request.GET.get('gia')
        from_price,to_price=price.split('-')
        if id_subcategory ==0:
            products=Product.objects.filter(price__gte=from_price).order_by('-public-day')
            if to_price !='':
                products=Product.objects.filter(price__gte=from_price,price__lt=to_price).order_by('-public_day')
                if keyword!='':
                    products=Product.objects.filter(price__gte=from_price,price__lt=to_price,name__contains=keyword).order_by('-public_day')
        else:
            products=Product.objects.filter(subcategory=id_subcategory,price__gte=from_price).order_by('-public_day')
            if to_price!='':
                products=Product.objects.filter(subcategory=id_subcategory,price__gte=from_price,price__lt=to_price).order_by('-public_day')
                if keyword!='':
                    products=Product.objects.filter(subcategory=id_subcategory,price__gte=from_price,price__lt=to_price,name__contains=keyword).order_by('-public_day')

    products_per_page = 9
    page = request.GET.get('page', 1)
    paginator = Paginator(products,products_per_page)
    try:
        products_pager = paginator.page(page)
    except PageNotAnInteger:
        products_pager = paginator.page(1)
    except EmptyPage:
        products_pager = paginator.page(paginator.num_pages)


    return render(request, 'product-list.html', {
        'subcategories': subcategories,
        'products':products,
        'products_pager':products_pager,
        'subcategory_name':subcategory_name,
        'cart_len':len(cart),
        'price':price,
    })

def san_pham(request,id_product):
    cart=Cart(request)
    product = Product.objects.get(pk=id_product)
    subcategory=product.subcategory
    related_products=Product.objects.filter(subcategory=subcategory.pk).exclude(pk=id_product).order_by('-public_day')[:20]
    subcategory_name=subcategory.name
    subcategory_id=subcategory.pk
    quantity=1
    if request.POST.get('btnthemvaogiohang'):
        quantity=int(request.POST.get('quantity'))
        them_vao_gio_hang(request,id_product,quantity)
        cart=Cart(request)


    return render(request, 'product-detail.html',{
        'product':product,
        'related_products':related_products,
        'subcategory_name':subcategory_name,
        'subcategory_id':subcategory_id,
        'cart_len':len(cart),
        'quantity':quantity,
    })

def read_rss(request):
    newfeed=feedparser.parse('https://feeds.feedburner.com/bedtimeshortstories/LYCF')
    entries=newfeed['entries']
    print(entries[0].keys())
    return render(request,'rss.html',{
        'entries':entries,
    })

def products_service(request):
    products = Product.objects.all()
    list_products = list(products.values('id','name', 'price', 'image'))
    return JsonResponse(list_products, safe=False)

class ProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.order_by('-public_day')
    serializer_class=ProductSerializer
    #permission_classes=[permissions.IsAdminUser]
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

def tim_kiem(request):
    cart=Cart(request)
    subcategories = SubCategory.objects.order_by('name')
    brands = Brand.objects.all()
    subcategory_name=''
    keyword=''
    if request.GET.get('tukhoa'):
        keyword=request.GET.get('tukhoa').strip()
        products=Product.objects.filter(name__contains=keyword).order_by('public_day')
        subcategory_name=f'All products ({products.count()})'
    
    if request.GET.get('gia'):
        price=request.GET.get('gia')
        keyword=request.GET.get('tukhoa')
        base_url=reverse('app_store:danh_muc',kwargs={'id_subcaegory':0})
        query_string=urlencode({
            'gia':price,
            'tukhoa':keyword,
        })
        url=f'{base_url}?{query_string}'
        return redirect(url)

    products_per_page = 9
    page = request.GET.get('page', 1)
    paginator = Paginator(products,products_per_page)
    try:
        products_pager = paginator.page(page)
    except PageNotAnInteger:
        products_pager = paginator.page(1)
    except EmptyPage:
        products_pager = paginator.page(paginator.num_pages)

        return render(request,'product-list.html',{
            'brands': brands,
            'subcategories': subcategories,
            'cart':cart,
            'subcategory_name':subcategory_name,
            'products_pager':products_pager,
            'products':products,
            'keyword':keyword,
        })
    else:
        return render(request,'product-list.html')
    