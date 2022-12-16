from LittleLemonAPI.models import Category, MenuItem, Cart
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer
from LittleLemonAPI.serializers import UserSerializer, GroupSerializer, CartSerializer

from rest_framework import generics, permissions, viewsets, status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response

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
    
    
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def manager(request):
    
    if request.method == 'POST':
        username = request.data['username']  # TODO: first check if data contains username
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)   # to delete: .remove(user)
            return Response({'message': f'user {username} was added to managers'}, status.HTTP_201_CREATED)    
        return Response({'message': 'username is mandatory'}, status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        managers = Group.objects.get(name='Manager')
        users_managers = managers.user_set.all().values('username')   # https://youtu.be/QrO-YgfWAOU?t=662
        return Response({'managers': users_managers}) 
    

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def delivery_crew(request):
    
    if request.method == 'POST':
        username = request.data['username']  # TODO: first check if data contains username
        if username:
            user = get_object_or_404(User, username=username)
            delivery = Group.objects.get(name='Delivery crew')
            delivery.user_set.add(user)  # to delete: .remove(user)
            return Response({'message': f'user {username} was added to delivery'}, status.HTTP_201_CREATED)    
        return Response({'message': 'username is mandatory'}, status.HTTP_406_NOT_ACCEPTABLE)
    
    elif request.method == 'GET':
        delivery = Group.objects.get(name='Delivery crew')
        users_delivery = delivery.user_set.all().values('username') 
        return Response({'delivery crew': users_delivery})
