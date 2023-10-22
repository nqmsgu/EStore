from django.shortcuts import render,redirect
from app_admin.form import *
from django.contrib.auth.models import User
from app_admin.models import *
from django.contrib.auth import *

def dang_ky_2(request):
    form_user=FormUser()
    form_profile=FormUserProfileInfo()

    chuoi_kq=''
    if request.POST.get('btnDangKy'):
        form_user=FormUser(data=request.POST)
        form_profile=FormUserProfileInfo(data=request.POST)
        if form_user.is_valid() and form_profile.is_valid():
            if form_user.cleaned_data['password']==form_user.cleaned_data['confirm_password']:
                user=form_user.save()
                user.is_superuser=1
                user.is_staff=1
                user.set_password(user.password)
                user.save()

                profile=form_profile.save(commit=False)
                profile.user=user
                profile.portfolio=form_profile.cleaned_data['portfolio']
                if 'image' in request.FILES:
                    profile.image=request.FILES['image']
                profile.save()

            else:
                chuoi_kq='''
                 <div class="alert alert-danger" role="alert">
                    Mật khẩu và xác nhận mật khẩu không khớp !!!
                </div>
            '''
        else:
            chuoi_kq='''
                 <div class="alert alert-danger" role="alert">
                    Đăng ký thất bại
                </div>
            '''

    return render(request, 'dang_ky.html',{
        'form_user':form_user,
        'form_profile':form_profile,
        'chuoi_kq':chuoi_kq,
    })

def dang_nhap_2(request):
    if request.user.is_authenticated is True:
        return redirect('app_admin:danh_sach_nguoi_dung_2')
    
    if request.POST.get('btnDangNhap'):
        username=request.POST.get('username')
        password=request.POST.get('password')
        nguoi_dung=authenticate(request,username=username,password=password)
        profile=UserProfileInfo.objects.filter(user=nguoi_dung)
        if nguoi_dung is not None:
            login(request,nguoi_dung)
            if profile.count()>0:
                dict_profile=profile.values()[0]
                dict_profile['image']=profile[0].image.url
                request.session['s_userprofile']=dict_profile
            return redirect('app_admin:danh_sach_nguoi_dung_2')

    return render(request, 'dang_nhap.html')

def dang_xuat_2(request):
    logout(request)
    if 's_userprofile' in request.session:
        del request.session['s_userprofile']
    return redirect('app_admin:dang_nhap_2')


def danh_sach_nguoi_dung_2(request):
    if request.user.is_authenticated is False:
        return redirect('app_admin:dang_nhap_2')

    ds_user=list(User.objects.all().values())
    ds_profile=list(UserProfileInfo.objects.all().values())
    for i in range(len(ds_user)):
        del (ds_user[i]['password'])
        ds_user[i].update(ds_profile[i])

    return render(request, 'danh_sach_nguoi_dung.html',{
        'ds_user':ds_user,
    })