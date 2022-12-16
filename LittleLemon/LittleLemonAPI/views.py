from LittleLemonAPI.models import Category, MenuItem, Cart
from django.contrib.auth.models import User, Group

from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer
from LittleLemonAPI.serializers import UserSerializer, GroupSerializer, CartSerializer

from rest_framework import generics, permissions, viewsets
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()  # NB: queries are lazy, thus all() is ok
    serializer_class = MenuItemSerializer
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # NB: queries are lazy, thus all() is ok
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        return []
        # if (self.request.method=='GET'):
        #     return []
        # return [permissions.IsAdminUser()]
        
class CartViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  
    serializer_class = CategorySerializer
