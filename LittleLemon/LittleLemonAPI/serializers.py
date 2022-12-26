from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Category, MenuItem, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):                                      
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
        

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())                      
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        
        
class CartSerializer(serializers.ModelSerializer):    
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    menuitem = serializers.SlugRelatedField(queryset=MenuItem.objects.all(), slug_field='title')                                      
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
 
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):

    orderitem = OrderItemSerializer(many=True, read_only=True, source='order')

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'date', 'total', 'orderitem']