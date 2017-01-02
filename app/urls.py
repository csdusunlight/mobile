'''
Created on 20161028

@author: lch
'''
from django.conf.urls import url,include

urlpatterns = [
    url(r'^news/$', 'app.views.get_news', name='app_news'),
    url(r'^slider/$', 'app.views.get_slider', name='app_slider'),
    url(r'^recom/$', 'app.views.get_recom', name='app_recom'),
    url(r'^detail/hongbao/$', 'app.views.get_content_hongbao', name='detail_hb'),
    url(r'^detail/youhuiquan/$', 'app.views.get_content_youhuiquan', name='detail_yhq'),
    url(r'^obtain_youhuiquan/$', 'app.views.exp_welfare_youhuiquan', name='obtain_youhuiquan'),
    
    url(r'^login/$', 'app.views.login'),
    url(r'^user/$', 'app.views.get_user_info', name='user_info'),
    
    url(r'^charge_json/$', 'app.views.charge_json'),
    url(r'^score_json/$', 'app.views.score_json'),
    url(r'^submit_order/$', 'app.views.submit_order'),
    url(r'^withdraw/$', 'app.views.withdraw'),
]
