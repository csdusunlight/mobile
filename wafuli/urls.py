'''
Created on 20160222

@author: lch
'''
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
# url_about = [
#     url(r'^aboutus/$', 'wafuli.views.aboutus', name="about"),
#     url(r'^report/$', 'wafuli.views.report'),
#     url(r'^coop/$', 'wafuli.views.coop'),
#     url(r'^notice/$', 'wafuli.views.notice'),
#     url(r'^contact/$', 'wafuli.views.contact'),
#     url(r'^statement/$', 'wafuli.views.statement'),
# ]
urlpatterns = [
    url(r'^$', 'wafuli.views.index', name='index'),
    url(r'^welfare_json/$', 'wafuli.welfare.welfare_json', name='welfare_json'),
    url(r'^finance_json/$', 'wafuli.welfare.finance_json', name='finance_json'),
    url(r'^task_json/$', 'wafuli.welfare.task_json', name='task_json'),
    url(r'^hongbao_json/$', 'wafuli.welfare.hongbao_json', name='hongbao_json'),
    url(r'^baoyou_json/$', 'wafuli.welfare.baoyou_json', name='baoyou_json'),
    url(r'^youhuiquan_json/$', 'wafuli.welfare.youhuiquan_json', name='youhuiquan_json'),
#    url(r'^(?P<board>\S+)/$', 'wafuli.views.board', name='board'),
    url(r'^finance/$', 'wafuli.views.finance', name='finance'),
    url(r'^finance/(?P<id>[0-9]*)/$', 'wafuli.views.finance', name='finance_detail'),
    url(r'^task/$', 'wafuli.views.task', name='task'),
    url(r'^task/(?P<id>[0-9]*)/$', 'wafuli.views.task', name='task_detail'),
    url(r'^welfare/(?:(?P<id>[0-9]*)/)?$', 'wafuli.welfare.welfare', name='welfare'),
    url(r'^welfare/(?:(?P<type>hb|yhq|by)/)?$', 'wafuli.welfare.welfare', name='welfare_list'),
     
#     url(r'^mall/$', 'wafuli.views.mall', name='mall'),
    url(r'^commodity/(?P<id>[0-9]*)/$', 'wafuli.views.commodity', name='commodity_detail'),
    url(r'^press/(?P<id>[0-9]*)/$', 'wafuli.views.press', name='press_detail'),
    url(r'^mallpage/$', 'wafuli.views.get_commodity_page', name='get_commodity_page'),
    url(r'^financepage/$', 'wafuli.views.get_finance_page', name='get_finance_page'),
    url(r'^taskpage/$', 'wafuli.views.get_task_page', name='get_task_page'),
    url(r'^welpage/$', 'wafuli.views.get_wel_page', name='get_wel_page'),
    url(r'^presspage/$', 'wafuli.views.get_press_page', name='get_press_page'),
    url(r'^aboutus/contactus/$', 'wafuli.views.aboutus_contactus', name="aboutus_contactus"),
    url(r'^aboutus/cooperation/$', 'wafuli.views.aboutus_cooperation', name="aboutus_cooperation"),
    url(r'^aboutus/statement/$', 'wafuli.views.aboutus_statement', name="aboutus_statement"),
    url(r'^strategy/$', 'wafuli.views.strategy', name="strategy"),
#     url(r'^exp_tf/$', 'wafuli.views.experience_taskandfinance', name='exp_tf'),
    url(r'^exp_wel_erweima/$', 'wafuli.welfare.exp_welfare_erweima', name='exp_welfare_erweima'),
    url(r'^exp_wel_openwindow/$', 'wafuli.welfare.exp_welfare_openwindow', name='exp_welfare_openwindow'),
    url(r'^exp_wel_youhuiquan/$', 'wafuli.welfare.exp_welfare_youhuiquan', name='exp_welfare_youhuiquan'),
    url(r'^get_coupon_success/$', 'wafuli.welfare.get_coupon_success', name='get_coupon_success'),
    url(r'^expsubmit/task/$', 'wafuli.views.expsubmit_task', name='expsubmit_task'),
    url(r'^expsubmit/finance/$', 'wafuli.views.expsubmit_finance', name='expsubmit_finance'),
    url(r'^lookup_order/$', 'wafuli.views.lookup_order', name='lookup_order'),
    url(r'^submit_order/$', 'wafuli.views.submit_order', name='submit_order'),
     
    url(r'^freshman/introduction/$', 'wafuli.views.freshman_introduction', name='freshman_introduction'),
    url(r'^freshman/award/$', 'wafuli.views.freshman_award', name='freshman_award'),
     
    url(r'^activity/recommend/$', 'wafuli.activity.recommend', name='activity_recommend'),
    url(r'^activity/recom_submit/$', 'wafuli.activity.recom_submit', name='activity_recom_submit'),
    url(r'^activity/recom_info/$', 'wafuli.activity.recom_info', name='activity_recom_info'),
    url(r'^activity/recom_rank/$', 'wafuli.activity.recom_rank', name='activity_recom_rank'),
     
    url(r'^activity/lottery/$', 'wafuli.activity.lottery', name='activity_lottery'),
    url(r'^activity/lottery/get_lottery/$', 'wafuli.activity.get_lottery', name='get_lottery'),
    
    url(r'^business/(?:list-page(?P<page>[0-9]*)/)?$', 'wafuli.views.business', name='business_list'),
    url(r'^information/(?:(?P<id>[0-9]*)/)?$', 'wafuli.views.information', name='information'),
    url(r'^information_json/$', 'wafuli.welfare.information_json', name='information_json'),
    
    url(r'^activity/$', 'wafuli.activity.activity', name='activity'),
    
    url(r'^invite_accept/$', 'account.views.invite_accept', name='invite_accept'),
    url(r'^screenshot/$', 'wafuli.views.display_screenshot', name='screenshot'),
    url(r'^task/introduction/$', TemplateView.as_view(template_name="m_task_introduction.html"),name='task_introduction'),
    
    url(r'^activity/Christmas/$', 'wafuli.activity.Christmas', name='activity_Christmas'),
#     url(r'^activity/Christmas/coupon/$', 'wafuli.activity.Christmas_coupon', name='Christmas_coupon'),
]
