from django.urls import path
from LittleLemonAPI import views

urlpatterns = [
    
    path('menu-items/', views.MenuItemsViewSet.as_view(
        {'get': 'list', 'post': 'create'}
        )),
    
    path('menu-items/<int:pk>/', views.MenuItemsViewSet.as_view(
        {'get': 'list', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        )),  
    
    path('category/', views.CategoryViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('category/<int:pk>/', views.CategoryViewSet.as_view({'get': 'retrieve'})), 
    
    path('groups/manager/users/', views.manager),
    path('groups/manager/users/<int:pk>/', views.manager),
    
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('groups/delivery-crew/users/<int:pk>/', views.delivery_crew),

    path('cart/menu-items/', views.cart),
    
    path('orders/', views.orders),
    
#     path('groups/', views.GroupViewSet.as_view({'get': 'list'})),
#     path('groups/<int:pk>/', views.GroupViewSet.as_view({'get': 'retrieve'})),     
#     path('cart/menu-items/', views.CartList.as_view()),
]