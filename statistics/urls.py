'''
Created on 20160223

@author: lch
'''
from django.conf.urls import url


urlpatterns = [
    url(r'^update', 'statistics.views.update', name='update'),
]