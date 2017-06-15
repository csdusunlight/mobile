'''
Created on 20161028

@author: lch
'''
from django.conf.urls import url,include

urlpatterns = [
    url(r'^news/$', 'app.views.get_news', name='app_news'),
    url(r'^slider/$', 'app.views.get_slider', name='app_slider'),
    url(r'^recom/$', 'app.views.get_recom', name='app_recom'),
    url(r'^get_today_num/$', 'app.views.get_today_num'),
    url(r'^detail/hongbao/$', 'app.views.get_content_hongbao', name='detail_hb'),
    url(r'^detail/youhuiquan/$', 'app.views.get_content_youhuiquan', name='detail_yhq'),
    url(r'^detail/task/$', 'app.views.get_content_task'),
    url(r'^detail/finance/$', 'app.views.get_content_finance'),
    url(r'^detail/information/$', 'app.views.get_content_information'),
    url(r'^obtain_youhuiquan/$', 'app.views.exp_welfare_youhuiquan'),
    url(r'^get_user_task_state/$', 'app.views.get_user_task_state'),
    url(r'^accept_task/$', 'app.views.accept_task'),
    
    url(r'^login/$', 'app.views.login'),
    url(r'^user/$', 'app.views.get_user_info', name='user_info'),
    
    url(r'^charge_json/$', 'app.views.charge_json'),
    url(r'^score_json/$', 'app.views.score_json'),
    url(r'^submit_order/$', 'app.views.submit_order'),
    url(r'^withdraw/$', 'app.views.withdraw'),
    
    url(r'^bind_bankcard/$', 'app.views.bind_bankcard'),
    url(r'^change_bankcard/$', 'app.views.change_bankcard'),
    url(r'^password_change/$', 'app.views.password_change'),
    
    url(r'^invite_to_balance/$', 'app.views.invite_to_balance'),
    url(r'^get_invite_info/$', 'app.views.get_invite_info'),
    
    url(r'^strategy/$', 'app.views.strategy'),
    
    url(r'^detail/press/$', 'app.views.get_content_press'),
    
    url(r'^signin/$', 'app.views.signin'),
    
    url(r'^submit_task/$', 'app.views.submit_task'),
    url(r'^submit_finance/$', 'app.views.submit_finance'),
    
    url(r'^activity/recom_submit/$', 'app.views.recom_submit'),
    url(r'^activity/recom_info/$', 'app.views.recom_info'),
    url(r'^activity/recom_rank/$', 'app.views.recom_rank'),
    
    url(r'^checkupdate/$', 'app.views.checkupdate'),
    
    url(r'^get_channel_project', 'app.views.get_channel_project',),
    url(r'^channel/$', 'app.views.account_channel'),
    
    url(r'^bank_name/$', 'app.views.get_bank_name'),
]
