#coding:utf-8
'''
Created on 2017年4月15日

@author: lch
'''
from django.shortcuts import render
from wafuli.models import Finance, UserEvent
from django.http.response import Http404, JsonResponse
import logging
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import datetime
from django.db import transaction
from account.models import DBlock
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger('wafuli')

@login_required
def account_channel(request):
    if not request.user.is_channel:
        raise Http404
    if request.method == 'POST':
        if not request.is_ajax():
            logger.warning("Expsubmit refused no-ajax request!!!")
            raise Http404
        code = -1
        url = ''
        
        news_id = request.POST.get('id', None)
        telnum = request.POST.get('telnum', '').strip()
        remark = request.POST.get('remark', '')
        term = request.POST.get('term', '').strip()
        amount = request.POST.get('amount',0)
        amount = int(float(amount))
        date_str = request.POST.get('time',0)
        time = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        if not (news_id and telnum):
            logger.error("news_id or news_type is missing!!!")
            raise Http404
        if len(telnum)>100 or len(remark)>200:
            code = 2
            msg = u'账号或备注过长！'
            result = {'code':code, 'msg':msg}
            return JsonResponse(result)
        news = None
        news = Finance.objects.get(pk=news_id)
        is_futou = news.is_futou
        info_str = "news_id:" + news_id + "| invest_account:" + telnum + "| is_futou:" + str(is_futou)
        logger.info(info_str)
        if is_futou:
            remark = u"复投：" + remark
        try:
            with transaction.atomic():
                db_key = DBlock.objects.select_for_update().get(index='event_key')
                if not is_futou and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
                    raise ValueError('This invest_account is repective in project:' + str(news.id))
                else:
                    UserEvent.objects.create(user=request.user, event_type='1', invest_account=telnum, invest_term=term, invest_time=time,
                                     invest_amount=amount, content_object=news, audit_state='1',remark=remark,)
                    code = 0
                    msg = u'提交成功，请通过用户中心查询！'
        except Exception, e:
            logger.info(e)
            code = 1
            msg = u'该注册手机号已被提交过，请不要重复提交！'
        result = {'code':code, 'msg':msg}
        return JsonResponse(result)
    else:
        flist = list(Finance.objects.filter(state='1', level__in=['channel','all']))
        return render(request, 'account/m_account_channel.html', {'flist':flist})