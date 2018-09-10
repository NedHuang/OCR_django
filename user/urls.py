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
    url(r'^reset_password/', views.reset_password, name = 'reset_password'),
    url(r'^edit_file/$',views.edit_file, name = 'edit_file'),
    url(r'^load_file/$', views.load_file, name ='load_file'),
    url(r'^next_page/$', views.next_page, name ='next_page'),
    url(r'^prev_page/$', views.prev_page, name ='prev_page'),
    url(r'^first_page/$', views.first_page, name ='first_page'),
    url(r'^last_page/$', views.last_page, name ='last_page'),
    url(r'^select_page/$', views.select_page, name ='select_page'),
    url(r'^save_change_to_server/$', views.save_change_to_server, name ='save_change_to_serversave_changesave_change'),
    url(r'^return_OCR_results/$', views.return_OCR_results, name ='return_OCR_results'),
    url(r'^get_my_data/$', views.get_my_data, name ='get_my_data'),
    url(r'^get_group_data/$', views.get_group_data, name ='get_group_data'),
    url(r'^change_resolution/$', views.change_resolution, name ='change_resolution'),
    url(r'^user_homepage/$', views.user_homepage, name ='user_homepage'),
    url(r'^guest_login/$', views.guest_login, name ='guest_login'),

    # url(r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root':'/Users/mingzhehuang/Desktop/OCR_django/user/static'}),
    # group
    url(r'^group_management/$', views.group_management, name='group_management'),

    url(r'^shared_group_management/$', views.shared_group_management, name='shared_group_management'),

    url(r'^create_group/$', views.create_group, name='create_group'),

    url(r'^(?P<group_guid>[0-9a-f-]+)$', views.edit_group, name='edit_group'),

    url(r'^delete_member/$', views.delete_member, name='delete_member'),
    # url(r'^(?P<group_id>[0-9a-f-]+)/delete_member/$', views.delete_member, name='delete_member'),

    url(r'^add_member/$', views.add_member, name='add_member'),

    url(r'^delete_group/$', views.delete_group, name='delete_group'),
    url(r'^share_file_to_group/$', views.share_file_to_group, name='share_file_to_group'),

    url(r'^show_shared_file_with_me/$', views.show_shared_file_with_me, name='show_shared_file_with_me'),

    url(r'^group_file_view/$', views.group_file_view, name='group_file_view'),
    url(r'^show_my_file/$', views.show_my_file, name='show_my_file'),
    url(r'^share_status/(?P<file_guid>[0-9a-f-]+)$', views.share_status_management, name='share_status_management'),
    url(r'^remove_share_record/$', views.remove_share_record, name='remove_share_record'),
    #改用户名
    url(r'^change_username/$', views.change_username, name='change_username'),
    #激活账户, p1 = guid, p2 = username
    url(r'^activate_account/$', views.activate_account, name = 'activate_account'),
]


urlpatterns += staticfiles_urlpatterns()