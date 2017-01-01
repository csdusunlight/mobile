#coding:utf-8
from wafuli.models import Advertisement_Mobile, Welfare, MAdvert, CouponProject,\
    Coupon, TransList
from datetime import datetime
from django.http.response import JsonResponse
from account.models import Userlogin, MyUser
from .tools import app_login_required
import hashlib
import time
from account.models import UserToken
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
host = 'http://test.wafuli.cn'
from django.core.urlresolvers import reverse
logger = logging.getLogger("wafuli")

def get_news(request):
    timestamp = request.GET.get('lastDate','')
    if not timestamp:
        return JsonResponse('',safe=False)
    lastDate = None
    try:
        lastDate = datetime.fromtimestamp(float(timestamp)/1000)
    except:
        lastDate = datetime.now()
    last_wel_list = Welfare.objects.filter(is_display=True,state='1',startTime__lt=lastDate).\
        exclude(type='baoyou').order_by("-startTime")[0:10]
    ret_list = []
    for wel in last_wel_list:
        marks = wel.marks.all()
        markc = len(marks)
        attr_dic = {
            'id':wel.id,
            'title':wel.title,
            'mark1': marks[0].name if markc > 0 else '',
            'mark2': marks[1].name if markc > 1 else '',
            'mark3': marks[2].name if markc > 2 else '',
            'pubDate': wel.startTime.strftime('%m-%d-%Y %H:%M:%S'),
            'image': host + wel.pic.url,
            'time': wel.time_limit,
            'source': wel.provider,
            'view': wel.view_count,
            'type':wel.type
        }
        ret_list.append(attr_dic)
    return JsonResponse({'code':0,'data':ret_list})
def get_slider(request):
    type = request.GET.get("type","index")
    if type=="task":
        adv_list = list(Advertisement_Mobile.objects.filter(location__in=['0','3'],is_hidden=False)[0:5])
    elif type=="finance":
        adv_list = list(Advertisement_Mobile.objects.filter(location__in=['0','4'],is_hidden=False)[0:5])
    else:
        adv_list = list(Advertisement_Mobile.objects.filter(location__in=['0','1'],is_hidden=False)[0:5])
    ret_list = []
    for adv in adv_list:
        attr_dic = {
            'id':adv.id,
            'image': host + adv.mpic.url,
            'priority': adv.news_priority,
            'pubDate': adv.pub_date,
        }
        ret_list.append(attr_dic)
    return JsonResponse({'code':0,'data':ret_list})
def get_recom(request):
    adv_today1 = MAdvert.objects.filter(location='1',is_hidden=False).first()
    adv_today2 = MAdvert.objects.filter(location='2',is_hidden=False).first()
    adv_today3 = MAdvert.objects.filter(location='3',is_hidden=False).first()
    ret_list = [{
        'id':adv_today1.id,
        'image': host + adv_today1.pic.url,
        'location': 1,
    },{
        'id':adv_today2.id,
        'image': host + adv_today2.pic.url,
        'location': 2,
    },{
        'id':adv_today3.id,
        'image': host + adv_today3.pic.url,
        'location': 3,
    }]
    return JsonResponse({'code':0,'data':ret_list})
def get_content_hongbao(request):
    ret_dict = {}
    id = request.GET.get('id', '')
    if not id:
        ret_dict['code'] = 1
        ret_dict['message'] = u"参数错误"
        return JsonResponse(ret_dict)
    
    try:
        wel = Welfare.objects.get(id=id)
    except:
        ret_dict['code'] = 2
        ret_dict['message'] = u"系统错误"
        return JsonResponse(ret_dict)
     
    if wel.type != "hongbao":
        ret_dict['code'] = 3
        ret_dict['message'] = u"类型错误"
        return JsonResponse(ret_dict)
    wel = wel.hongbao
    strategy = wel.strategy.replace('"/media/', '"' + host + '/media/')
    ret_dict = {
        'code':0,
        'image': host + wel.pic.url,
        'strategy':strategy,
        'num': wel.view_count,
        'time': wel.time_limit,
        'ismobile': wel.isonMobile,
        'url': wel.exp_url if not wel.isonMobile else (host + wel.exp_code.url),
        'title':wel.title
    }
    return JsonResponse(ret_dict)
def get_content_youhuiquan(request):
    ret_dict = {}
    id = request.GET.get('id', '')
    if not id:
        ret_dict['code'] = 1
        ret_dict['message'] = u"参数错误"
        return JsonResponse(ret_dict)
    
    try:
        wel = Welfare.objects.get(id=id)
    except:
        ret_dict['code'] = 2
        ret_dict['message'] = u"系统错误"
        return JsonResponse(ret_dict)
     
    if wel.type != "youhuiquan":
        ret_dict['code'] = 3
        ret_dict['message'] = u"类型错误"
        return JsonResponse(ret_dict)
    wel = wel.couponproject
    if wel.ctype == '2':
        wel.left_count = wel.coupons.filter(user__isnull=True).count()
    else:
        wel.left_count = u"充足"
    strategy = wel.strategy.replace('/media/', host + '/media/')
    ret_dict = {
        'code':0,
        'image': host + wel.pic.url,
        'strategy':strategy,
        'num': wel.left_count,
        'time': wel.time_limit,
        'url': wel.exp_url,
        'title':wel.title,
    }
    return JsonResponse(ret_dict)


@app_login_required
@csrf_exempt
def exp_welfare_youhuiquan(request):
    user = request.user
    result = {}
    wel_id = request.POST.get('id', None)
    if not wel_id:
        logger.error("wel_id is missing!!!")
        result['code'] = 4
        result['msg'] = u'参数错误！'
        return JsonResponse(result)
    wel = CouponProject.objects.get(id=wel_id)
    if wel.state != '1':
        result['code'] = 3
        result['msg'] = u'该活动已结束！'
        return JsonResponse(result)
    draw_count = user.user_coupons.filter(project=wel).count()
    if draw_count >= wel.claim_limit:
        result['code'] = 2
        result['msg'] = u'抱歉，您已达到领取次数上限！'
        return JsonResponse(result)
    coupon = None
    if wel.ctype == '2':
        coupon = Coupon.objects.filter(project=wel,user__isnull=True).first()
        if coupon is None:
            result['code'] = 1
            result['msg'] = u'抱歉，该优惠券已被领取完了'
            return JsonResponse(result)
        coupon.user = user
        coupon.time = datetime.now()
        coupon.save(update_fields=['user','time'])
    else:
        coupon = Coupon.objects.create(user=user, project=wel)
    result['code'] = 0
    result['coupon_id'] = coupon.id
    result['exchange_code'] = coupon.exchange_code
    return JsonResponse(result)

@never_cache
@csrf_exempt
def login(request):
    """
    Displays the login form and handles the login action.
    """
    result = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = MyUser.objects.get_by_natural_key(username)
            if not user.check_password(password):
                raise ValidationError('Password Error!',code='NotPass')
        except Exception as e:
            result.update(code=1)
        else:
            salt = "wafuli20161116"
            expire = int(time.time()*1000) + 2*7*24*60*60*1000
            token = hashlib.md5(str(username) + str(password) + salt + str(expire)).hexdigest()
            UserToken.objects.filter(user=user).delete()
            UserToken.objects.create(user=user,token=token,expire=expire)
            result.update(code=0, token=token, expire=expire)
            user.last_login_time = user.this_login_time
            user.this_login_time = datetime.now()
            Userlogin.objects.create(user=user,)
            user.save(update_fields=["last_login_time", "this_login_time"])
        return JsonResponse(result)


@app_login_required
@csrf_exempt
def get_user_info(request):
    user = request.user
    result = {'code':0, 'accu_income':user.accu_income, 'balance':user.balance, 
              'mobile':user.mobile, 'userimg':user.id%4, 'scores':user.scores}
    return JsonResponse(result)

@app_login_required
def charge_json(request):
    user = request.user
    logger.info("@@@@@@@@@@@@" + user.mobile)
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get('type', '0'))
    start = 6*count
    item_list = TransList.objects.filter(user=request.user, transType=type)[start:start+6]
    data = []
    for con in item_list:      
        i = {"reason":con.reason,
             "amount":con.transAmount,
             "date":con.time.strftime("%Y-%m-%d"),
             }
        if type == '1':
            event = con.user_event
            if event:
                state = event.get_audit_state_display()
            else:
                state = u"无"
            i.update({"state":state,})   
        data.append(i)
    return JsonResponse(data, safe=False)