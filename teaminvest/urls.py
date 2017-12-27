#coding:utf-8
'''
Created on 20170703

@author: lch
'''

from django.conf.urls import url
from teaminvest import views

urlpatterns = [
    url(r'^submit/$', views.teaminvest_submit, name="teaminvest_submit"),
]
