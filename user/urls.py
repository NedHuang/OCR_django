"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url,include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import staticfiles
urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name = 'register'),
    url(r'^logout/', views.logout, name = 'logout'),
    url(r'^main/', views.main, name = 'main'),
    url(r'^upload/',views.upload, name = 'upload'),
    url(r'^file_management/',views.file_management, name = 'file_management'),
    # url(r'^anonymous/',views.anonymous, name = 'anonymous'),
    url(r'^ajax/', views.ajax, name = 'ajax'),
    url(r'^delete_file/', views.delete_file, name = 'delete_file'),
    url(r'^share_file/', views.share_file, name = 'share_file'),
    url(r'^resetByUsernameForm/', views.resetByUsernameForm, name = 'resetByUsernameForm'),
    url(r'^edit_file/$',views.edit_file, name = 'edit_file'),
    url(r'^load_file/', views.load_file, name ='load_file'),



    # url(r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root':'/Users/mingzhehuang/Desktop/OCR_django/user/static'}),
]


urlpatterns += staticfiles_urlpatterns()