from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign2text/', views.sign2text, name='sign2text'),
    path('text2sign/', views.text2sign, name='text2sign'),
    path('api/upload', views.upload_and_convert, name='video-upload'),
    path('api/text-to-video', views.text_to_video, name='get-text'),
    path('api/audio-to-text', views.audio_to_text, name='audio-to-text'),
    path('api/output_gloss', views.output_gloss, name='output-gloss'),
    path('api/compare/', views.compare_sign_by_url, name='compare-sign'), #1
    path('api/upload_compare', views.upload_and_compare, name='upload-and-compare'),
]