#coding:utf-8
'''
Created on 20160614

@author: lch
'''
from django.shortcuts import render

from wafuli.models import Advertisement, UserWelfare, UserEvent, LotteryRecord
import logging
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from wafuli_admin.models import RecommendRank
import datetime
from wafuli.tools import weighted_random
from account.transaction import charge_score, charge_money
from wafuli.data import AwardTable
from django.db.models import Q
from django.contrib.auth.decorators import login_required
logger = logging.getLogger('wafuli')


def activity(request):
    return render(request, 'm_activity.html')

def recommend(request):
    return render(request, 'm_activity_recommend.html')

@login_required
def recom_submit(request):
    user = request.user
    if request.method == "POST":
        if not request.is_ajax():
            logger.warning("Experience refused no-ajax request!!!")
            raise Http404
        result = {}
        sumbit_num_today = UserWelfare.objects.filter(user=user, date__gte=datetime.date.today()).count()
        if sumbit_num_today>=5:
            result['code'] = 4
            result['res_msg'] = u'每天最多只能提交5条哦，请明日再来！'
            return JsonResponse(result)
        title = request.POST.get('title', '')
        url = request.POST.get('url', '')
        reason = request.POST.get('reason', '')
        if not (title and url) or len(title)>200 or len(url)>200 or len(reason)>200:
            result['code'] = 3
            result['res_msg'] = u'输入参数长度有误！'
        else:
            try:
                wel = UserWelfare.objects.create(user=user, title=title,url=url,reason=reason)
                UserEvent.objects.create(user=user, event_type='6', content_object=wel, audit_state='1')
            except Exception as e:
                result['code'] = 2
                result['res_msg'] = u'重复提交或数据有误！'
                logger.warning(e)
            else:
                result['code'] = 0
                result['res_msg'] = u'提交成功！'
        return JsonResponse(result)
    else:
        ref_url = request.META.get('HTTP_REFERER',"")
        context = {}
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_activity_recom_submit.html', context)
def recom_rank(request):
    if not request.is_ajax():
        return render(request, 'm_activity_recom_rank.html')
    else:
        res={'code':0,}
        count = request.GET.get("count", 0)
        try:
            count = int(count)
        except ValueError:
            count = 0
        item_list = []
        start = 12*count
        item_list = RecommendRank.objects.all()[start:start+12]
        data = []
        for con in item_list:
            username = con.user.get_abbre_name()
            i = {"username":username,
                 "num":con.acc_num,
                 "rank":con.rank,
                 "award":con.award,
                 }
            data.append(i)
        return JsonResponse(data, safe=False) 

@login_required
def recom_info(request):
    if not request.is_ajax():
        ref_url = request.META.get('HTTP_REFERER',"")
        context = {}
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_activity_recom_info.html', context)
    else:
        user = request.user
        count = request.GET.get("count", 0)
        try:
            count = int(count)
        except ValueError:
            count = 0
        item_list = []
        start = 12*count
        item_list = UserEvent.objects.filter(user=user,event_type='6')[start:start+12]
        data = []
        for con in item_list:
            i = {"title":con.content_object.title,
                 "time":con.time.strftime("%Y-%m-%d"),
                 "state":con.get_audit_state_display(),
                 }
            data.append(i)
        return JsonResponse(data, safe=False) 


def get_recommend_rank_page(request):
    res={'code':0,}
    user = request.user
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('activity_recommend')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 3)
    try:
        size = int(size)
    except ValueError:
        size = 3
    if not page or size <= 0:
        raise Http404
    item_list = []
    item_list = RecommendRank.objects.all()[0:12]
    
    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        username = con.user.get_abbre_name()
        i = {"username":username,
             "num":con.acc_num,
             "rank":con.rank,
             "award":con.award,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def lottery(request):
    user = request.user
    record_list = LotteryRecord.objects.all()[0:20]
    record_list_c = []
    for record in record_list:
        record_list_c.append({
             'user': record.user.get_abbre_name(),
             'date': record.date.strftime("%H:%M:%S"),
             'award':record.award,               
        })
    context = {"record":record_list_c};
    return render(request, 'm_activity_lottery.html',context)

def get_lottery(request):
    user = request.user
    if request.method != "POST" or not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    result = {}
    if not user.is_authenticated():
        result['code'] = -1
        result['url'] = reverse('login') + "?next=" + reverse('activity_lottery')
        return JsonResponse(result)
    if user.scores < 10:
        result['code'] = -2
        return JsonResponse(result)
    trans = charge_score(user, '1', 10, u"积分抽奖")
    if not trans:
        result['code'] = -3
        logger.error("lottery 10 scores charge error!")
        return JsonResponse(result)
    event = UserEvent.objects.create(user=user, event_type='7', audit_state='1')
    trans.user_event = event
    trans.save(update_fields=['user_event'])
    award_list = [(1, 61), (2, 30), (3, 6), (4, 2), (5, 1), (6, 0),]
    itemid = weighted_random(award_list)
    translist = None
    if itemid == 2:
        translist = charge_score(user, '0', 10, u'抽奖获奖')
    elif itemid == 3:
        translist = charge_score(user, '0', 50, u'抽奖获奖')
    elif itemid == 4:
        translist = charge_money(user, '0', 80, u'抽奖获奖')
    elif itemid == 5:
        translist = charge_money(user, '0', 200, u'抽奖获奖')
    if itemid!=1 and not translist:
        result['code'] = -4
        logger.error("Get lottery award charge error!")
        result['res_msg'] = "记账失败！"
    else:
        result['code'] = 0
        result['itemid'] = itemid
        if itemid != 1:
            LotteryRecord.objects.create(user=user, award = AwardTable.get(itemid, u'未知'))
            translist.user_event = event
            translist.save(update_fields=['user_event'])
    return JsonResponse(result)

