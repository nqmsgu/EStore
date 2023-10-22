from django.shortcuts import render, redirect
from app_customer.models import *
from django.contrib.auth.hashers import PBKDF2PasswordHasher,Argon2PasswordHasher,BCryptSHA256PasswordHasher
from app_cart.cart import *
from app_cart.models import *
from app_store.models import *
from django.template.loader import render_to_string
from django.conf import settings
import pdfkit,os,base64
from app_customer.customer_libs import *


salt='123'
def dang_nhap_dang_ky(request):
    cart=Cart(request)
    if 's_khachhang' in request.session:
        return redirect('app_store:trang_chu')

    chuoi_kq_dang_nhap = ''
    if request.POST.get('btnDangNhap'):
        hasher=PBKDF2PasswordHasher()
        email = request.POST.get('email').strip()
        mat_khau = hasher.encode(request.POST.get('mat_khau').strip(),salt)

        khach_hang = Customer.objects.filter(email=email, password=mat_khau)
        if khach_hang.count() > 0:
            dict_khach_hang = khach_hang.values()[0]
            request.session['s_khachhang'] = dict_khach_hang
            return redirect('app_store:trang_chu')
        else:
            chuoi_kq_dang_nhap = '''
                <div class="alert alert-danger" role="alert">
                    Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.
                </div>
                '''
    

    # Lấy thông tin tỉnh/tp, quận/huyện, phường/xã
    du_lieu = read_json_internet('http://api.laptrinhpython.net/vietnam')

    # Tỉnh/TP
    list_provinces = []
    str_districts = []
    str_wards = []
    list_districts_2 = []
    for province in du_lieu:
        list_provinces.append(province['name'])
        # Quận/Huyện
        list_districts_1 = []
        for dictrict in province['districts']:
            d = dictrict['prefix'] + ' ' + dictrict['name']
            list_districts_1.append(d)
            list_districts_2.append(d)
            # Phường/Xã
            list_wards = []
            for ward in dictrict['wards']:
                w = ward['prefix'] + ' ' + ward['name']
                list_wards.append(w)
            else:
                str_wards.append('|'.join(list_wards))
        else:
            str_districts.append('|'.join(list_districts_1))

    chuoi_kq_dang_ky = ''
    if request.POST.get('btnDangKy'):
        ho = request.POST.get('ho').strip()
        ten = request.POST.get('ten').strip()
        email = request.POST.get('email').strip()
        mat_khau = request.POST.get('mat_khau').strip()
        xac_nhan_mat_khau = request.POST.get('xac_nhan_mat_khau').strip()
        dien_thoai = request.POST.get('dien_thoai').strip()
        dia_chi_tmp = request.POST.get('dia_chi').strip()
        tinh_thanh=request.POST.get('tinh_thanh')
        quan_huyen=request.POST.get('quan_huyen')
        phuong_xa=request.POST.get('phuong_xa')
        hasher=PBKDF2PasswordHasher()

        dia_chi=str(dia_chi_tmp)+','+ str(phuong_xa)+','+ str(quan_huyen)+','+ str(tinh_thanh)
        if mat_khau == xac_nhan_mat_khau:
            Customer.objects.create(first_name=ho,
                                    last_name=ten,
                                    email=email,
                                    password=hasher.encode(mat_khau,salt),
                                    phone=dien_thoai,
                                    address=dia_chi)

            chuoi_kq_dang_ky = '''
                <div class="alert alert-success" role="alert">
                    Đăng ký thành viên thành công.
                </div>
                '''
        else:
            chuoi_kq_dang_ky = '''
                <div class="alert alert-danger" role="alert">
                    Mật khẩu và Xác nhận mật khẩu không khớp.
                </div>
                '''

    return render(request, 'login.html', {
        'chuoi_kq_dang_ky': chuoi_kq_dang_ky,
        'chuoi_kq_dang_nhap': chuoi_kq_dang_nhap,
        'cart_len':len(cart),
        'provinces': tuple(list_provinces),
        'str_districts': tuple(str_districts),
        'str_wards': tuple(str_wards),
        'list_districts': list_districts_2,
    })


def dang_xuat(request):
    if 's_khachhang' in request.session:
        del request.session['s_khachhang']
    return redirect('app_customer:dang_nhap_dang_ky')

def thong_tin_cua_toi(request):
    cart=Cart(request)
    khach_hang=request.session.get('s_khachhang')
    if 's_khachhang' not in request.session:
        return redirect('app_customer:dang_nhap_dang_ky')
    
    orders=Order.objects.filter(customer=khach_hang['id'])
    dict_orders = {}
    for order in orders:
        order_items = list(OrderItem.objects.filter(order=order.pk).values())
        for order_item in order_items:
            product = Product.objects.get(pk=order_item['product_id'])
            order_item['product_name'] = product.name
            order_item['product_image'] = product.image
            order_item['total'] = order.total
        else:
            dict_order_items = {
                order.pk: order_items
            }
            dict_orders.update(dict_order_items)
    
    if request.POST.get('btnUpdatePass'):
        hasher=PBKDF2PasswordHasher()
        obj_khach_hang=Customer.objects.get(pk=khach_hang['id'])
        password=hasher.encode(request.POST.get('password'),salt)
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')
        if obj_khach_hang.password==password:
            if new_password==confirm_password:
                obj_khach_hang.password=hasher.encode(new_password,salt)
                obj_khach_hang.save()



    return render(request, 'my-account.html',{
        'cart_len':len(cart),
        'orders':orders,
        'dict_orders':dict_orders,
        'khach_hang':khach_hang,
    })

def xuat_bao_cao_don_hang(request,order_id):
    if 's_khachhang' not in request.session:
        return redirect('app_customer:dang_nhap_dang_ky')
    khach_hang=request.session.get('s_khachhang')
    order=Order.objects.get(customer=khach_hang['id'],pk=order_id)
    order_date=order.created.strftime('%d-%m-%Y %H:%M:%S')
    order_items = list(OrderItem.objects.filter(order=order_id).values())
    for order_item in order_items:
        product = Product.objects.get(pk=order_item['product_id'])
        order_item['product_name'] = product.name

        with open(settings.MEDIA_ROOT+str(product.image),'rb') as img_file:
            img_string=base64.b64encode(img_file.read())

        order_item['product_image'] = img_string.decode('utf-8')
        order_item['total'] = order.total

    html_string=render_to_string('report_order.html',{
        'order_date':order_date,
        'customer':khach_hang,
        'order_items':order_items,
        'pk':order_id,
    })

    config=pdfkit.configuration(wkhtmltopdf=os.path.join(settings.STATIC_ROOT,'wkhtmltox/bin/wkhtmltopdf.exe'))
    file_name=f'DH{order_id}.pdf'
    folder_report=os.path.join(settings.MEDIA_ROOT,'report/')
    path_report=folder_report+file_name
    pdfkit.from_string(html_string,path_report,configuration=config)


    return redirect(f'/media/report/{file_name}')