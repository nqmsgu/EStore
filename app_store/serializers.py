from rest_framework import serializers, status
from rest_framework.response import Response
from app_store.models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    subcategory = serializers.IntegerField(source='subcategory_id')

    class Meta:
        model = Product
        fields = '__all__'
    
    def create(self, validated_data):
        return Product.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.subcategory = validated_data.get('subcategory', instance.subcategory)
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.price_origin = validated_data.get('price_origin', instance.price_origin)
        instance.image = validated_data.get('image', instance.image)
        instance.content = validated_data.get('content', instance.content)
        instance.viewed = validated_data.get('viewed', instance.viewed)
        instance.save()
        return instance
