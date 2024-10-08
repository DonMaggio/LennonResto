"""
URL configuration for lennonproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lennonapp.urls')),
    path('api-authorization/', include('rest_framework.urls')), #autenticacion desde la API
    path('accounts/', include('django.contrib.auth.urls')), #autenticacion manual
    #path('auth/', include('djoser.urls')),
    #path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""
Available endpoints de Djoser 

/users/

/users/me/

/users/confirm/

/users/resend_activation/

/users/set_password/

/users/reset_password/

/users/reset_password_confirm/

/users/set_username/

/users/reset_username/

/users/reset_username_confirm/

/token/login/ (Token Based Authentication)

/token/logout/ (Token Based Authentication)

/jwt/create/ (JSON Web Token Authentication)

/jwt/refresh/ (JSON Web Token Authentication)

/jwt/verify/ (JSON Web Token Authentication)

"""