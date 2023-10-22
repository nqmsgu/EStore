from django.shortcuts import render,redirect,get_object_or_404
from app_cart.cart import *
from app_store.models import *
from django.views.decorators.http import require_POST
from app_customer.models import *
from app_cart.models import *
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings

def gio_hang(request):
    cart=Cart(request)

    if request.POST.get('btnCapNhatGioHang'):
        cart_new={}
        for c in cart:
            quantity_new=int(request.POST.get('quantity_2_' + str(c['product'].pk)))
            if quantity_new!=0:
                product_cart={
                    str(c['product'].pk):{
                    'quantity':quantity_new,
                    'price':str(c['product'].price),
                    'coupon':str(c['coupon'])
                    }
                }
                cart_new.update(product_cart)
                c['quantity']=quantity_new
            else:
                cart.remove(c['product'])
        else:
            request.session['cart']=cart_new

    
    return render(request,'cart.html',{
        'cart':cart,
        'cart_len':len(cart),
    })

@require_POST
def mua_ngay(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    if request.POST.get('quantity'):
        quantity=int(request.POST.get('quantity'))
        cart.add(product,quantity)
    return redirect('app_cart:gio_hang')

@require_POST
def xoa_san_pham(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    cart.remove(product)
    return redirect('app_cart:gio_hang')

def thanh_toan(request):
    cart=Cart(request)
    if len(cart) == 0:
        return redirect('app_cart:gio_hang')
    
    ds_ma_giam_gia=[
        {'TTTH':0.8},
        {'MINH':0.5},
    ]
    ma_giam_gia=" "
    if request.POST.get('btnmagiamgia'):
        ma_giam_gia=request.POST.get('ma_giam_gia').strip()
        for dict_ma_giam_gia in ds_ma_giam_gia:
            if ma_giam_gia in dict_ma_giam_gia:
                giam_gia=dict_ma_giam_gia[ma_giam_gia]
                cart_new={}
                for c in cart:
                    product_cart={
                        str(c['product'].pk):{
                            'quantity':c['quantity'],
                            'price':str(c['product'].price),
                            'coupon':str(giam_gia)
                        }
                    }
                    cart_new.update(product_cart)
                    c['coupon']=giam_gia
                else:
                    request.session['cart']=cart_new


    if request.POST.get('btnDatHang'):
        khach_hang=Customer.objects.get(pk=request.session.get('s_khachhang')['id'])
        
        order=Order()
        order.customer=khach_hang
        order.total=cart.get_final_total_price()
        order.save()

        list_products=[]
        for c in cart:
            OrderItem.objects.create(order=order,
                                     product=c['product'],
                                     price=c['price'],
                                     quantity=c['quantity'],
                                     discount=c['quantity']*c['price']*(1-c['coupon']),
                                     total_price=c['total_price']
                                     )
            list_products.append(c['product'].name)
        
        subject= f'Đặt hàng thành công #{ order.pk }'
        content= ''
        for product in list_products:
            content+= f'- {product}\n'
        sender=settings.EMAIL_HOST_USER
        receivers=[khach_hang.email,sender]
        send_mail(subject,content,sender,receivers)

        cart.clear()
        cart=Cart(request)
        return render(request,'result.html',{
            'cart':cart,
            'cart_len':len(cart),
        })

    return render(request,'checkout.html',{
        'cart':cart,
        'cart_len':len(cart),
        'ma_giam_gia':ma_giam_gia,
    })

@require_POST
def them_vao_gio_hang(request,product_id,quantity):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    cart.add(product,quantity)
    