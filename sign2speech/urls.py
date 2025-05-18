from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('video.urls')),
    path('', TemplateView.as_view(template_name='video/Sign2Text.html'), name='sign2text'),
    path('sign2text', TemplateView.as_view(template_name='video/Sign2Text.html'), name='sign2text'),
    path('text2sign', TemplateView.as_view(template_name='video/Text2Sign.html'), name='text2sign'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)