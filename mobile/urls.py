"""mobile URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url('^app/', include('app.urls')),
    url(r'^', include('wafuli.urls',)),
    url('^account/', include('account.urls')),
    url('^Admin/', include('wafuli_admin.urls')),
    url(r'^ueditor/',  include('DjangoUeditor.urls' )),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^statistic/', include('statistics.urls', namespace='statistic'),),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^weixin/', include('weixin.urls')),
    url(r'^restapi/', include('restapi.urls')),
    url(r'^teaminvest/', include('teaminvest.urls')),
#     url(r'^test/$', 'wafuli.views.index', name='captcha-refresh'),
]

from django.conf.urls.static import static
from mobile import settings
#urlpatterns += static(settings.STATIC_URL , document_root = settings.STATIC_ROOT )
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT )