from django.urls import path
from app_visualization.views import *

app_name = 'app_visualization'
urlpatterns = [
    path('visualization/', visualization, name='visualization'),
]
