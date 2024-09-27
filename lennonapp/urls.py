from django.urls import path, include
from .views import MenuItemView, SingleItemView, CustomerCartView, OrdersView, SingleOrderview
from .views import UserRegisterView
from .views import CustomPasswordChangeView, CreateMenuItemView
from rest_framework.documentation import include_docs_urls

#View Sets
from .views import ProductViewSet
from . import views
from rest_framework.routers import DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='productos')


urlpatterns = [
    path('home', views.home, name='home'),
    #path('secret', views.secret),

    #rutas para el menu
    path('menu', MenuItemView.as_view(), name='menu'),
    path('cart/menu-items', CustomerCartView.as_view(), name='cart'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>', SingleOrderview.as_view(), name='single-order'),

    #Gestion de la carta
    path('menu-items/add', CreateMenuItemView.as_view(), name='add-item-menu'),
    path('menu-items/<int:pk>/', SingleItemView.as_view(), name='menu-edit'),
    
    #gestion de usuarios
    #path('users/', UserView.as_view(), name='users'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('accounts/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    #path('groups/manager/users', ManagerUsersView.as_view()),
    #path('groups/manager/users/<int:pk>', ManagerSingleUserView.as_view()),
    #path('groups/delivery/users', DeliveryUserView.as_view()),
    #path('groups/delivery/users/<int:pk>', DeliveryUserSingleView.as_view()),

    #documentacion
    path('docs', include_docs_urls(title='Lennon Resto'), name='docs'),

    #generacion de token, solo POST
    path('api-token-auth', obtain_auth_token, name='token'),
] 

urlpatterns += router.urls