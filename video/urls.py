from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/upload', views.upload_and_convert, name='video-upload'),
]