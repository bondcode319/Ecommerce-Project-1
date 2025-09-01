from rest_framework import serializers
from .models import Product
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 
                 'stock', 'imageUrl', 'created_date', 'owner', 'is_available']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user