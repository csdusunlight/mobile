from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'wafuli_admin.views.index', name='admin_index'),
    url(r'^indexpage/$', 'wafuli_admin.views.get_admin_index_page', name='get_admin_index_page'),
    url(r'^admin_task/$', 'wafuli_admin.views.admin_task', name='admin_task'),
    url(r'^admin_finance/$', 'wafuli_admin.views.admin_finance', name='admin_finance'),
    url(r'^finance_page/$', 'wafuli_admin.views.get_admin_finance_page', name='get_admin_finance_page'),
    url(r'^task_page/$', 'wafuli_admin.views.get_admin_task_page', name='get_admin_task_page'),
    url(r'^admin_user/$', 'wafuli_admin.views.admin_user', name='admin_user'),
    url(r'^userpage/$', 'wafuli_admin.views.get_admin_user_page', name='get_admin_user_page'),
    url(r'^admin_withdraw/$', 'wafuli_admin.views.admin_withdraw', name='admin_withdraw'),
    url(r'^withpage/$', 'wafuli_admin.views.get_admin_with_page', name='get_admin_with_page'),
    url(r'^admin_score$', 'wafuli_admin.views.admin_score', name='admin_score'),
    url(r'^scorepage/$', 'wafuli_admin.views.get_admin_score_page', name='get_admin_score_page'),
    url(r'^admin_recommend_return/$', 'wafuli_admin.activity.admin_recommend_return', name='admin_recommend_return'),
    url(r'^return_recommend_page/$', 'wafuli_admin.activity.get_admin_recommend_return_page', name='get_admin_recommend_return_page'),
    
    url(r'^deliver_coupon/$', 'wafuli_admin.coupon.deliver_coupon', name='deliver_coupon'),
    url(r'^get_project_list/$', 'wafuli_admin.coupon.get_project_list', name='get_project_list'),
    url(r'^parse_file/$', 'wafuli_admin.coupon.parse_file', name='parse_file'),
    url(r'^admin_coupon/$', 'wafuli_admin.coupon.admin_coupon', name='admin_coupon'),
    url(r'^admin_coupon_page/$', 'wafuli_admin.coupon.get_admin_coupon_page', name='get_admin_coupon_page'),
    
    url(r'^admin_charge/$', 'wafuli_admin.views.admin_charge', name='admin_charge'),
    url(r'^chargepage/$', 'wafuli_admin.views.get_admin_charge_page', name='get_admin_charge_page'),
]