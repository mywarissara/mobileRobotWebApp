from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('index', views.index),
    path('setting', views.setting),
    path('facereg', views.take_picture),
    path('register', views.register),
    path('users', views.admin),
    path('save_point', views.save_point),
    path('video', views.camera_live),
    path('snap', views.snapshot),
    path('counter', views.counter),
    path('complete', views.complete),
    path('get_user_info', views.get_user_info)

]