from django.contrib import admin
from app_store.models import *
from datetime import datetime
from django.utils.html import format_html

def Change_public_day(modeladmin,request,queryset):
    queryset.update(public_day=datetime.now())
    
Change_public_day.short_description='Change public_day of selected products to current time'

class Category_admin(admin.ModelAdmin):
    list_display=('name',)

class Subcategory_admin(admin.ModelAdmin):
    list_display=('e_name','e_category_name')

    @admin.display(description='Tên danh mục con')
    def e_name(self,obj):
        return f'{obj.name}'
    
    @admin.display(description='Tên danh mục cha')
    def e_category_name(self,obj):
        return f'{obj.category.name}'

class Product_admin(admin.ModelAdmin):
    exclude=('public_day','viewed',)
    #list_display=('name','price','price_origin','public_day','viewed')
    list_display=('e_name','e_price','e_price_origin','e_public_day','e_viewed','e_subcategory','e_image')
    list_filter=('public_day',)
    search_fields=('name__contains',)
    actions=[Change_public_day]

    @admin.display(description='Tên sản phẩm')
    def e_name(self,obj):
        return f'{obj.name}'

    @admin.display(description='Giá bán')
    def e_price(self,obj):
        return f'{"{:,}".format(int(obj.price))}'
    
    @admin.display(description='Giá gốc')
    def e_price_origin(self,obj):
        return f'{"{:,}".format(int(obj.price_origin))}'

    @admin.display(description='Ngày phát hành')
    def e_public_day(self,obj):
        return f'{obj.public_day.strftime("%d/%m/%y %H:%M:%S")}'
    
    @admin.display(description='Lượt xem')
    def e_viewed(self,obj):
        return f'{obj.viewed}'
    
    @admin.display(description='Hình ảnh')
    def e_image(self,obj):
        return format_html(f'<img src="{obj.image.url}" alt={obj.name} style="height:45px;width:45px" />')
    
    @admin.display(description='Danh mục con')
    def e_subcategory(self,obj):
        return f'{obj.subcategory.name}'




admin.site.register(Category,Category_admin)
admin.site.register(SubCategory,Subcategory_admin)
admin.site.register(Product,Product_admin)
admin.site.site_header='Estore administration'
