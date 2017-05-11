#coding:utf-8
'''
Created on 2016年8月1日

@author: lch
'''
from django.shortcuts import render
from django.http.response import Http404, HttpResponse
from wafuli.models import Welfare, Advertisement_Mobile, Press, Hongbao, Baoyou, CouponProject,\
    Company, Coupon, Information, Task, Finance, Mark, Commodity, UserTask
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db.models import Q,F
import logging
from wafuli_admin.models import RecommendRank
from account.models import MyUser
import re
from .tools import listing, get_weixin_params
from django.contrib.auth.decorators import login_required
from wafuli.tools import update_view_count
from datetime import timedelta
logger = logging.getLogger('wafuli')
import datetime

def welfare(request, id=None, type=None):
    if not id:
        wel_list = Welfare.objects.filter(state='1', is_display=True)
        if type:
            type = str(type)
            if type == 'hb':
                return render(request, 'm_hongbao.html')
            elif type == 'yhq':
                return render(request, 'm_youhuiquan.html')
            elif type == 'by':
                return render(request, 'm_baoyou.html')
        raise Http404
    elif id:
        id = int(id)
        try:
            wel = Welfare.objects.get(id=id)
        except Welfare.DoesNotExist:
            raise Http404(u"该页面不存在")
#         other_wel_list = Welfare.objects.filter(is_display=True, state='1').order_by('-view_count')[0:10]
#         if wel.type != "baoyou":
#             url = request.get_full_path()
#             weixin_params = get_weixin_params(url)
#             context['weixin_params'] = weixin_params
        update_view_count(wel)
        template = ''
        if wel.type == "youhuiquan":
            template = 'm_detail_youhuiquan.html'
            wel = wel.couponproject
            if wel.ctype == '2':
                wel.left_count = wel.coupons.filter(user__isnull=True).count()
            else:
                wel.left_count = u"充足"
        elif wel.type == "hongbao":
            template = 'm_detail_hongbao.html'
            wel = wel.hongbao
        elif wel.type == "baoyou":
            template = 'm_detail_hongbao.html'
            wel = wel.baoyou
        ref_url = request.META.get('HTTP_REFERER',"")
        context = {'news':wel,'type':'Welfare',}
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, template, context)
    
def exp_welfare_erweima(request):
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    result = {}
    if not request.user.is_authenticated():
        url = reverse('user_guide') + '?next=' + request.META['HTTP_REFERER']
        result['url'] = url
        result['code'] = '0'
        return JsonResponse(result)
    wel_id = request.GET.get('id', None)
    wel_type = request.GET.get('type', None)
    if not wel_id or not wel_type:
        logger.error("wel_id is missing!!!")
        raise Http404
    wel_id = int(wel_id)
    wel_type = str(wel_type)
    model = globals()[wel_type]
    wel = model.objects.get(id=wel_id)
    update_view_count(wel)
    if wel_type == 'Welfare':
        if wel.type == "hongbao":
            wel = wel.hongbao
        elif wel.type == "baoyou":
            wel = wel.baoyou
    if wel.isonMobile:
        result['url'] = wel.exp_code.url
    else:
        logger.error(str(model) + ":" + str(wel.id) + " is not onMobile wel !!!")
        raise Http404
    result['code'] = '1'
    if wel_type == "Task" and not wel.is_forbidden:
        obj, created = UserTask.objects.get_or_create(user=request.user, task=wel)
        if created:
            if wel.left_num <=1:
                wel.state = '2'
            wel.left_num = F("left_num")-1
            wel.save(update_fields=["left_num","state"])
    return JsonResponse(result)

@login_required
def exp_welfare_openwindow(request):
    wel_id = request.GET.get('id', None)
    wel_type = request.GET.get('type', None)
    if not wel_id or not wel_type:
        logger.error("wel_id or type is missing!!!")
        raise Http404
    wel_id = int(wel_id)
    wel_type = str(wel_type)
    model = globals()[wel_type]
    wel = model.objects.get(id=wel_id)
    if wel_type == "Task" and not wel.is_forbidden:
        obj, created = UserTask.objects.get_or_create(user=request.user, task=wel)
        if created:
            if wel.left_num <=1:
                wel.state = '2'
            wel.left_num = F("left_num")-1
            wel.save(update_fields=["left_num","state"])
    update_view_count(wel)
    url = wel.exp_url_mobile
    if url=='':
        js = ''' 
        <script>
        alert("本项目仅限电脑端体验，请前往电脑端。");
        window.history.back();
        </script>
        
        '''
    else:
        js =''' 
        <script src="/static/js/mui.min.js"></script>
        <script>
        mui.init();
        mui.ready(function(){
                window.location.href="
        ''';
        js += url + '";});</script>'
    return HttpResponse(js)

def exp_welfare_youhuiquan(request):
    user = request.user
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    result = {}
    if not user.is_authenticated():
        url = reverse('user_guide') + '?next=' + request.META['HTTP_REFERER']
        result['url'] = url
        result['code'] = '0'
        return JsonResponse(result)
    wel_id = request.GET.get('id', None)
    if not wel_id:
        logger.error("wel_id is missing!!!")
        raise Http404
    wel = CouponProject.objects.get(id=wel_id)
    if wel.state != '1':
        result['code'] = '4'
        return JsonResponse(result)
    draw_count = user.user_coupons.filter(project=wel).count()
    if draw_count >= wel.claim_limit:
        result['code'] = '2'
        return JsonResponse(result)
    coupon = None
    if wel.ctype == '2':
        coupon = Coupon.objects.filter(project=wel,user__isnull=True).first()
        if coupon is None:
            result['code'] = '1'
            return JsonResponse(result)
        coupon.user = user
        coupon.time = datetime.datetime.now()
        coupon.save(update_fields=['user','time'])
    else:
        coupon = Coupon.objects.create(user=user, project=wel)
    result['code'] = '3'
    result['coupon_id'] = coupon.id
    return JsonResponse(result)

def get_coupon_success(request):
    id = request.GET.get('id',None)
    if not id:
        raise Http404
    coupon = Coupon.objects.get(id=id)
    return render(request, 'm_get_coupon_success.html', {'coupon':coupon})

def welfare_json(request):
    count = int(request.GET.get('count', 0))
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    start = 6*count
    now = datetime.datetime.now()
    to = now - timedelta(days=1)
    begin = now - timedelta(days=55)
    wel_list = Welfare.objects.filter(is_display=True,state='1',startTime__range=(begin,to)).\
        exclude(type='baoyou').order_by('-view_count')[start:start+6]
    for wel in wel_list:
        marks = wel.marks.all()[0:3]
        mlist = []
        for mark in marks:
            mlist.append(mark.name)
        data.append({
            'url':wel.url,
            'picurl':wel.pic.url,
            'title':wel.title,
            'view_count':wel.view_count,
            'provider':wel.provider,
            'time_limit':wel.time_limit,
            'marks':mlist,
            'is_hot':wel.is_hot()
        })
    return JsonResponse(data,safe=False)

def finance_json(request):
    count = request.GET.get('count', 0)
    type = request.GET.get('type', '0')
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    count = int(count)
    type = str(type)
    start = 6*count
    wel_list = Finance.objects.filter(state='1', level__in=['normal','all'])
    if type == '0':
        wel_list = wel_list.order_by('-pub_date')[start:start+6]
    else:
        wel_list = wel_list.filter(f_type=type).order_by('-view_count')[start:start+6]
    for wel in wel_list:
        marks = wel.marks.all()[0:3]
        mlist = []
        for mark in marks:
            mlist.append(mark.name)
        data.append({
            "title":wel.title,
            "interest":wel.interest,
            "amount":wel.amount_to_invest,
            "time":wel.investTime,
            "benefit":wel.benefit,
            "url":wel.url,
            'picurl':wel.pic.url,
            'id':wel.id,
            'marks':mlist,
        })
    return JsonResponse(data,safe=False)

def task_json(request):
    count = request.GET.get('count', 0)
    type = request.GET.get('type', '0')
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    count = int(count)
    type = str(type)
    start = 6*count
#     item_list = Task.objects.filter(state='1')
    item_list = Task.objects.filter(state__in=['1','2'])
    if type == '1':
        item_list = item_list.filter(type="junior")
    elif type == '2':
        item_list = item_list.filter(type="middle")
    elif type == '3':
        item_list = item_list.filter(type="senior")
    item_list = item_list.order_by("state","is_forbidden","-pub_date")[start:start+6]
    for wel in item_list:
        data.append({
            "title":wel.title,
            "time":wel.time_limit,
            "view_count":wel.view_count,
            "url":wel.url,
            'picurl':wel.pic.url,
            'provider':wel.provider,
            'money':wel.moneyToAdd,
            'score':wel.scoreToAdd,
            'num':wel.left_num,
            'state':wel.state,
            'is_forbidden':wel.is_forbidden,
            'id':wel.id,
            })
    return JsonResponse(data,safe=False)
            
def hongbao_json(request):
    count = int(request.GET.get('count', 0))
    type = request.GET.get('type', u"全部")
    data = []
    count = int(count)
    start = 6*count
    wel_list = Hongbao.objects
    if type != u"全部":
        mark = None
        try:
            mark = Mark.objects.get(name=type)
        except Mark.DoesNotExist:
            logger.error("The mark: " + type + " doesn't exists!")
            wel_list = []
        else:
            wel_list = mark.welfare_set
    if wel_list:
        wel_list = wel_list.filter(is_display=True,state='1')[start:start+6]
    for wel in wel_list:
        marks = wel.marks.all()[0:3]
        mlist = []
        for mark in marks:
            mlist.append(mark.name)
        data.append({
            'url':wel.url,
            'picurl':wel.pic.url,
            'title':wel.title,
            'view_count':wel.view_count,
            'provider':wel.provider,
            'time_limit':wel.time_limit,
            'marks':mlist,
            'id':wel.id
        })
    return JsonResponse(data,safe=False)

def youhuiquan_json(request):
    count = int(request.GET.get('count', 0))
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    start = 6*count
    wel_list = CouponProject.objects.filter(is_display=True,state='1')[start:start+6]
    for wel in wel_list:
        marks = wel.marks.all()[0:3]
        mlist = []
        for mark in marks:
            mlist.append(mark.name)
        data.append({
            'url':wel.url,
            'picurl':wel.pic.url,
            'title':wel.title,
            'view_count':wel.view_count,
            'provider':wel.provider,
            'time_limit':wel.time_limit,
            'marks':mlist,
            'id':wel.id
        })
    return JsonResponse(data,safe=False)

def baoyou_json(request):
    count = int(request.GET.get('count', 0))
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    start = 6*count
    wel_list = Baoyou.objects.filter(is_display=True,state='1')[start:start+6]
    for wel in wel_list:
        marks = wel.marks.all()[0:3]
        mlist = []
        for mark in marks:
            mlist.append(mark.name)
        data.append({
            'url':wel.url,
            'picurl':wel.pic.url,
            'title':wel.title,
            'mprice':wel.mprice,
            'nprice':wel.nprice,
            'desc':wel.desc,
            'id':wel.id,
            'exp_url':wel.exp_url_mobile,
        })
    return JsonResponse(data,safe=False)

def information_json(request):
    count = int(request.GET.get('count', 0))
    type = request.GET.get('type', 0)
    type = int(type)
    data = []
    count = int(count)
    start = 6*count
    info_list = Information.objects.filter(is_display=True)
    if type == 0:
        info_list = info_list.filter(type="wahangqing")
    if type == 1:
        info_list = info_list.filter(type="wagushi")
    if type == 2:
        info_list = info_list.filter(type="washuju")
    if type == 3:
        info_list = info_list.filter(type="wahuodong")
    info_list = info_list[start:start+6]
    for info in info_list:
        data.append({
            'url':info.url,
            'picurl':info.pic.url,
            'title':info.title,
            'summary':info.summary,
            'view_count':info.view_count,
            'id':info.id
        })
    return JsonResponse(data,safe=False)
