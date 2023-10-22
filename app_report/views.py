from django.http import JsonResponse
from django.shortcuts import render
from app_store.models import *
from django.core import serializers

def report_with_flexmonster(request):
    return render(request,'report_with_flexmonster.html')

def pivot_data(request):
    dataset = Product.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)
