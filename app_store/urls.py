from django.urls import path
from app_store.views import *

app_name = 'app_store'
urlpatterns = [
    path('lien-he/', lien_he, name='lien_he'),
    path('', trang_chu, name='trang_chu'),
    path('danh-muc/<int:id_subcategory>/', danh_muc, name='danh_muc'),
    path('san-pham/<int:id_product>/', san_pham, name='san_pham'),
    path('read-rss/', read_rss, name='read_rss'),
    path('products-service/', products_service, name='products_service'),
    path('tim-kiem/', tim_kiem, name='tim_kiem'),
]
