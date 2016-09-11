#coding:utf-8
'''
Created on 2016年8月1日

@author: lch
'''
from django.shortcuts import render
from django.http.response import Http404, HttpResponse
from wafuli.models import Welfare, Advertisement, Press, Hongbao, Baoyou, CouponProject,\
    Company, Coupon, Information, Task, Finance
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db.models import Q
import logging
from wafuli_admin.models import RecommendRank
from account.models import MyUser
import re
from .tools import listing
from django.contrib.auth.decorators import login_required
logger = logging.getLogger('wafuli')
import datetime

def welfare(request, id=None, page=None, type=None):
    if not id:
        if not page:
            page = 1
        else:
            page = int(page)
        full_path = str(request.get_full_path())
        path_split = []
        if 'list-page' in full_path:
            path_split = re.split('list-page\d+',full_path)
        elif '?' in full_path:
            path_split = full_path.split('?')
            path_split[1] = '?' + path_split[1]
        else:
            path_split=[full_path, '']
        page_dic = {}
        ref_dic = {}
        page_dic['pre_path'] = path_split[0]
        page_dic['suf_path'] = path_split[1]
        wel_list = Welfare.objects.filter(is_display=True)
        state = request.GET.get('state', '1')
        full_path_ = re.sub(r'/list-page\d+&?', '', full_path, 1)
        ref_path1 = re.sub(r'state=\d+&?', '', full_path_, 1)
        ref_path2, num = re.subn(r'state=\d+', 'state=2', full_path_)
        if num == 0:
            if '?' in ref_path2:
                ref_path2 += '&state=2'
            else:
                ref_path2 += '?state=2'
        if ref_path1[-1] == '?' or ref_path1[-1] == '&':
            ref_path1 = ref_path1[:-1]
        ref_dic = {'state':state, 'ref_path1':ref_path1, 'ref_path2':ref_path2,}
        if state:
#             ref_path = re.sub(r'state=\d+', 'state=1', full_path, 1)
            state = str(state)
            wel_list = wel_list.filter(state=state)
        if type:
            type = str(type)
            if type == 'hb':
                wel_list = wel_list.filter(type="hongbao")
            elif type == 'yhq':
                wel_list = wel_list.filter(type="youhuiquan")
            elif type == 'by':
                wel_list = wel_list.filter(type="baoyou")
        search_key = request.GET.get('key', '')
        if search_key:
            wel_list = wel_list.filter(Q(title__contains=search_key)|Q(company__name__contains=search_key))
        business = request.GET.get('business', '')
        if business:
            wel_list = wel_list.filter(company__name=business)
        wel_list, page_num = listing(wel_list, 12, int(page))
        if page_num < 10:
            page_list = range(1,page_num+1)
        else:
            if page < 6:
                page_list = range(1,8) + ["...",page_num]
            elif page > page_num - 5:
                page_list = [1,'...'] + range(page_num-6, page_num+1)
            else:
                page_list = [1,'...'] + range(page-2, page+3) + ['...',page_num]
        page_dic['page_list'] = page_list
        ad_list = Advertisement.objects.filter(Q(location='0')|Q(location='2'),is_hidden=False)[0:8]
        strategy_list = Press.objects.filter(type='2')[0:10]
        hot_wel_list = Welfare.objects.filter(is_display=True, state='1').order_by('-view_count')[0:2]
        business_list = Company.objects.order_by('-view_count')[0:10]
        hot_info = Information.objects.filter(is_display=True).order_by('-view_count').first()
        context = {
            'wel_list':wel_list,
            'business_list':business_list,
            'ad_list':ad_list,
            'strategy_list':strategy_list,
            'page_dic':page_dic,
            'ref_dic':ref_dic,
            'hot1':hot_wel_list[0],
            'hot2':hot_wel_list[1],
            'info':hot_info,
        }
        ranks = RecommendRank.objects.all()[0:6]
        for i in range(len(ranks)):
            key = 'rank'+str(i+1)
            username = ranks[i].user.username
            if len(username) > 4:
                username = username[0:4] + '****'
            else:
                username = username + '****'
            acc_num = ranks[i].acc_num
            context.update({key:{'username':username,'acc_num':str(acc_num)+u'条'}})
        return render(request, 'zeroWelfare.html', context)
    elif id:
        id = int(id)
        try:
            wel = Welfare.objects.get(id=id)
        except Welfare.DoesNotExist:
            raise Http404(u"该页面不存在")
        other_wel_list = Welfare.objects.filter(is_display=True, state='1').order_by('-view_count')[0:10]
        template = 'detail-common.html'
        if wel.type == "youhuiquan":
            template = 'detail-youhuiquan.html'
            wel = wel.couponproject
        elif wel.type == "hongbao":
            wel = wel.hongbao
        elif wel.type == "baoyou":
            wel = wel.baoyou
        return render(request, template,{'news':wel,'type':'Welfare', 'other_wel_list':other_wel_list})
    
def exp_welfare_erweima(request):
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    result = {}
    if not request.user.is_authenticated():
        url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
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
    url = wel.exp_url
    js = "<script>window.location.href='"+url+"';</script>"
    return HttpResponse(js)

def exp_welfare_youhuiquan(request):
    user = request.user
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    result = {}
    if not user.is_authenticated():
        url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
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
    if wel.ctype == '2':
        coupon = Coupon.objects.filter(project=wel,user__isnull=True).first()
        if coupon is None:
            result['code'] = '1'
            return JsonResponse(result)
        coupon.user = user
        coupon.time = datetime.datetime.now()
        coupon.save(update_fields=['user','time'])
    else:
        Coupon.objects.create(user=user, project=wel)
    result['code'] = '3'
    return JsonResponse(result)

def welfare_json(request):
    count = int(request.GET.get('count', 0))
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    start = 6*count
    wel_list = Welfare.objects.filter(is_display=True,state='1').order_by('-view_count')[start:start+6]
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
        })
    return JsonResponse(data,safe=False)