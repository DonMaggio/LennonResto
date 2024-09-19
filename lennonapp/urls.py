from django.urls import path, include
from .views import MenuItemView, SingleItemView, CustomerCartView, OrdersView, SingleOrderview, ManagerUsersView, ManagerSingleUserView, DeliveryUserView, DeliveryUserSingleView
from rest_framework.documentation import include_docs_urls

#View Sets
from .views import ProductViewSet
from . import views
from rest_framework.routers import DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='productos')


urlpatterns = [
    #path('home', views.home, name='home'),
    path('secret', views.secret),

    #rutas para el menu
    path('menu', MenuItemView.as_view()),
    path('menu-items/<int:pk>/', SingleItemView.as_view()),
    path('cart/menu-items', CustomerCartView.as_view()),
    path('orders/', OrdersView.as_view()),
    path('orders/<int:pk>', SingleOrderview.as_view()),

    #gestion de usuarios
    path('groups/manager/users', ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>', ManagerSingleUserView.as_view()),
    path('groups/delivery/users', DeliveryUserView.as_view()),
    path('groups/delivery/users/<int:pk>', DeliveryUserSingleView.as_view()),


    #documentacion
    path('docs', include_docs_urls(title='Lennon Resto')),

    #generacion de token, solo POST
    path('api-token-auth', obtain_auth_token),
] 

urlpatterns += router.urls