'''
Created on 20161225

@author: lch
'''
from django.conf.urls import url,include

urlpatterns = [
    url(r'^$', 'weixin.views.weixin', name='token_verify'),
    url(r'^bind-user/$', 'weixin.views.bind_user', name='bind-user'),
#     url(r'^slider/$', 'app.views.get_slider', name='app_slider'),
#     url(r'^recom/$', 'app.views.get_recom', name='app_recom'),
#     url(r'^detail/hongbao/$', 'app.views.get_content_hongbao', name='detail_hb'),
#     url(r'^detail/youhuiquan/$', 'app.views.get_content_youhuiquan', name='detail_yhq'),
#     url(r'^obtain_youhuiquan/$', 'app.views.exp_welfare_youhuiquan', name='obtain_youhuiquan'),
#     
#     url(r'^login/$', 'app.views.login', name='login'),
#     url(r'^user/$', 'app.views.get_user_info', name='user_info'),
]
