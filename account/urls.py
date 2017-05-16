from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', 'account.views.account', name='account_index'),
    url(r'^account_settings/$', 'account.views.account_settings', name='account_settings'),
    url(r'^get_nums/$', 'account.views.get_nums', name='get_nums'),
    url(r'^welfare/$', 'account.views.welfare', name='account_welfare'),
    url(r'^score/$', 'account.views.score', name='account_score'),
    url(r'^score_json/$', 'account.views.score_json', name='score_json'),
    url(r'^charge/$', 'account.views.charge', name='account_charge'),
    url(r'^charge_json/$', 'account.views.charge_json', name='charge_json'),
    url(r'^exchange/$', 'account.views.exchange', name='account_exchange'),
    url(r'^exchange/morescore/$', 'account.views.exchange_morescore', name="exchange_morescore"),
    url(r'^exchange/introduction/$', 'account.views.exchange_introduction', name="exchange_introduction"),
    url(r'^exchange/questions/$', 'account.views.exchange_questions', name="exchange_questions"),
    url(r'^commodity_json/$', 'account.views.commodity_json', name='commodity_json'),
    url(r'^welfare_json/$', 'account.views.get_user_welfare_json', name='get_user_welfare_json'),
#     url(r'money/$', 'account.views.money', name='account_money'),
#     url(r'user/$', 'account.views.user', name='account_user'),
    url(r'^coupon/$', 'account.views.coupon', name='account_coupon'), 
    url(r'^user_coupon_json/$', 'account.views.user_coupon_json', name='user_coupon_json'),
    url(r'^coupondetail/$', 'account.views.get_user_coupon_exchange_detail', name='get_user_coupon_exchange_detail'),
    url(r'^useCoupon/$', 'account.views.useCoupon', name='account_useCoupon'),
    url(r'^security/$', 'account.views.security', name='account_security'),
    url(r'^withdraw/$', 'account.views.withdraw', name='account_withdraw'),
    url(r'^invite/$', 'account.views.invite', name='account_invite'),
    url(r'^invitepage/$', 'account.views.get_user_invite_page', name='get_user_invite_page'),
    url(r'^message/(?:(?P<id>[0-9]*)/)?$', 'account.views.message', name='account_message'),
    url(r'^message_json/$', 'account.views.message_json', name='message_json'),
    url(r'^user-guide/$', 'account.views.user_guide', name='user_guide'),
    url(r'^register/$', 'account.views.register', name='register'),
    url(r'^login/$', 'account.views.login', {'template_name': 'registration/m_login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logged_out.html', 'next_page':'account_index'}, name='logout'),
    url(r'^signin/$', 'account.views.signin', name='signin'),
    url(r'^signin_record/$', 'account.views.signin_record', name='signin_record'),
    url(r'^password_change/$', 'account.views.password_change', name='password_change'),
    url(r'^change_pay_password/$', 'account.views.change_pay_password', name='change_pay_password'),
    url(r'^active_email/$', 'account.views.active_email', name='active_email'),
    url(r'^bind_zhifubao/$', 'account.views.bind_zhifubao', name='bind_zhifubao'),
    url(r'^change_zhifubao/$', 'account.views.change_zhifubao', name='change_zhifubao'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', 'account.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^verifyemail/$', 'account.views.verifyemail', name='verifyemail'),
    url(r'^verifymobile/$', 'account.views.verifymobile', name='verifymobile'),
    url(r'^verifyusername/$', 'account.views.verifyusername', name='verifyusername'),
    url(r'^verifyinviter/$', 'account.views.verifyinviter', name='verifyinviter'),
    url(r'^phoneImageV/$', 'account.views.phoneImageV', name='phoneImageV'),
#    url(r'verifytelcode/$', 'account.views.verifytelcode', name='verifytelcode'),
    url(r'^callback/$', 'account.views.callbackby189', name='callback'),
    
    url(r'^customService/$', TemplateView.as_view(template_name="account/m_custom_service.html"),name='account_custom_service'),
    url(r'^joinQQGroup/$', TemplateView.as_view(template_name="account/m_join_QQGroup.html"),name='account_join_QQGroup'),
    
    url(r'^channel/$', 'account.channel.account_channel',name='account_channel'),
    url(r'^vip/$', 'account.vip.vip',name='account_vip'),
    url(r'^vip_intro/$', 'account.vip.vip_intro',name='vip_intro'),
]