'''
Created on 20161028

@author: lch
'''
from django.conf.urls import url,include

urlpatterns = [
    url(r'^$', 'app.views.index', name='app_index'),
    url(r'^welfare_json/$', 'wafuli.welfare.welfare_json', name='welfare_json'),
]
