from django.urls import path, include
from .views import MenuItemView, SingleItemView, CustomerCartView, OrdersView, SingleOrderview
from rest_framework.documentation import include_docs_urls

#View Sets
from .views import ProductViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='productos')


urlpatterns = [
    #path('home', views.home, name='home'),

    #rutas para el menu
    path('menu', MenuItemView.as_view()),
    path('menu-items/<int:pk>/', SingleItemView.as_view()),
    path('cart/menu-items', CustomerCartView.as_view()),
    path('orders/', OrdersView.as_view()),
    path('orders/<int:pk>', SingleOrderview.as_view()),

    #documentacion
    path('docs', include_docs_urls(title='Lennon Resto')),
] 

urlpatterns += router.urls