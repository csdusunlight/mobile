
from django.conf.urls import url, include
from restapi import views
from wafuli import rest

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^translist/$', views.TranslistList.as_view(),),
    url(r'^investlog/$', views.TeamProjectInvestLogList.as_view()),
    url(r'^investlog/(?P<pk>[0-9]+)/$', views.TeamProjectInvestLogDetail.as_view(), kwargs={'partial':True}),
    url(r'^backlog/$', views.BackLogList.as_view()),
    url(r'^backlog/(?P<pk>[0-9]+)/$', views.BackLogDetail.as_view(), kwargs={'partial':True}),
]
