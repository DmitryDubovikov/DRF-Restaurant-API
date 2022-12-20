from LittleLemonAPI.models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer
from LittleLemonAPI.serializers import CartSerializer

from rest_framework import generics, permissions, viewsets, status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
import datetime

class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()  # NB: queries are lazy, thus all() is ok
    serializer_class = MenuItemSerializer
    
    ordering_fields = ['price']
    filterset_fields = ['price', 'category']
    search_fields = ['title']
    
    def get_permissions(self):
        if (self.request.method=='GET'):
            return []
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not self.request.user.groups.filter(name='Manager').exists():
            return [permissions.IsAdminUser()]  # cannot return false
        return [permissions.IsAuthenticated()]
        
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # NB: queries are lazy, thus all() is ok
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if (self.request.method=='GET'):
            return []
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not self.request.user.groups.filter(name='Manager').exists():
            return [permissions.IsAdminUser()]  # cannot return false
        return [permissions.IsAuthenticated()]
        
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()  
    serializer_class = CartSerializer
    
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def manager(request, pk=None):    
    if request.method == 'POST':
        username = request.data['username']  
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)   # to delete: .remove(user)
            return Response({'message': f'user {username} was added to managers'}, status.HTTP_201_CREATED)    
        return Response({'message': 'username is mandatory'}, status.HTTP_400_BAD_REQUEST)    
    elif request.method == 'GET':
        managers = Group.objects.get(name='Manager')
        users_managers = managers.user_set.all().values('username')   # https://youtu.be/QrO-YgfWAOU?t=662
        return Response({'managers': users_managers}, status.HTTP_200_OK) 
    elif request.method == 'DELETE':
        if pk:
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)   
            return Response({'message': f'user {user.username} was deleted from managers'}, status.HTTP_200_OK)    
        return Response({'message': 'id is mandatory'}, status.HTTP_400_BAD_REQUEST)
            
    

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delivery_crew(request, pk=None):    
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
        return Response({'delivery crew': users_delivery}, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if pk:
            user = get_object_or_404(User, pk=pk)
            delivery = Group.objects.get(name='Delivery crew')
            delivery.user_set.remove(user)   
            return Response({'message': f'user {user.username} was deleted from delivery'}, status.HTTP_200_OK)    
        return Response({'message': 'id is mandatory'}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def cart(request):    
    if request.method == 'POST':
        menu_item = MenuItem.objects.get(title=request.data['menu_item'])
        quantity = int(request.data['quantity'])
        cart_item = Cart.objects.create(  
            quantity=quantity, unit_price=menu_item.price, price=menu_item.price*quantity, 
            user_id=request.user.id, menuitem_id=menu_item.id
            )
        return Response({'message': f'menuitem {menu_item} was added to cart of user {request.user.id}'}, status.HTTP_201_CREATED)
    elif request.method == 'GET':
        user_cart = Cart.objects.filter(user_id=request.user.id).values()
        return Response({'user cart': user_cart}, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        user_cart = Cart.objects.filter(user_id=request.user.id)
        user_cart.delete()
        return Response({'message': f'cart of user {request.user.id} was flushed'}, status.HTTP_200_OK)
    
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def orders(request):  
    if request.method == 'POST':
        
        # create order
        user_cart_items = Cart.objects.filter(user_id=request.user.id)
        total = user_cart_items.aggregate(Sum('price'))
        order = Order.objects.create(
            user=request.user, date=datetime.datetime.now(), total=total['price__sum']
        )
        
        # bulk create order items        
        creates = []
        for item in user_cart_items.values():
            creates.append(
                OrderItem(order_id=order.id, menuitem_id=item['menuitem_id'], quantity=item['quantity'], 
                unit_price=item['unit_price'], price=item['price'])
            )
        OrderItem.objects.bulk_create(creates)
        
        # flush cart
        user_cart_items.delete()
        
        return Response({'message': f'order was created for user {request.user.id}'}, status.HTTP_201_CREATED)
    elif request.method == 'GET':
        
        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all().values()
        elif request.user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew_id=request.user.id).values()
        else:        
            orders = Order.objects.filter(user_id=request.user.id).values()
        
        return Response({'orders': orders}, status.HTTP_200_OK)    
    
    elif request.method == 'DELETE':
        pass
    
    
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def order_detail(request, pk=None):  
    
    # if request.method == 'PUT':
    #     if request.user.groups.filter(name='Manager').exists():
    #         pass
    #     else:
    #         return Response({'message': f'you are not authorized to modify order {pk}'}, status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'PATCH':
        if request.user.groups.filter(name='Manager').exists():
            order = Order.objects.get(pk=pk)
            order.status = False if request.data['status']=='0' else True
            order.delivery_crew_id = int(request.data['delivery_crew'])
            order.save()
            return Response({'message': f'status is {order.status} and deilvery is {order.delivery_crew_id} for order {pk}'}, status.HTTP_200_OK)
        elif request.user.groups.filter(name='Delivery crew').exists():
            order = Order.objects.get(pk=pk)
            order.status = False if request.data['status']=='0' else True
            order.save()
            return Response({'message': f'status is set to {order.status} for order {pk}'}, status.HTTP_200_OK)
        else:
            return Response({'message': f'you are not authorized to modify order {pk}'}, status.HTTP_401_UNAUTHORIZED)
        
    elif request.method == 'GET':
        # if customer and it is not his order - display error, else - show order items
        order = Order.objects.get(pk=pk)
        if not request.user.groups.filter(name='Manager').exists() \
            and not request.user.groups.filter(name='Delivery crew').exists() \
            and not request.user.id==order.user_id \
            or (request.user.groups.filter(name='Delivery crew').exists() and not order.delivery_crew_id==request.user.id):
            return Response({'message': f'you are not authorized to view order {pk}'}, status.HTTP_401_UNAUTHORIZED)
        else:
            order_items = OrderItem.objects.filter(order_id=order.id)
            return Response({'order items': order_items.values()}, status.HTTP_200_OK)
        
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response({'message': f'order {pk} was deleted'}, status.HTTP_200_OK)
        else:
            return Response({'message': f'only managers can delete orders'}, status.HTTP_401_UNAUTHORIZED)            
    
    
