"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path,include
from WorkingImage.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index, name="home"),
    path('adding/', ImageAdding.as_view(), name="adding"),
    path('', include('django.contrib.auth.urls')),
	path('panel/', Panel, name="panel"),
	path(r'^delete-entry/(?P<pk>\d+)/$', DeleteView.as_view(), name='delete_view'),
	path('optimize/<int:pk>/', Optimize, name='optimize'),
	path('optimizing/<int:pk>', Optimizing, name="optimizing"),
    path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    path(r'^statics/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
