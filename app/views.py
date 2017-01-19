#coding:utf-8
from wafuli.models import Advertisement_Mobile, Welfare, MAdvert, CouponProject,\
    Coupon, TransList, ScoreTranlist, Commodity, ExchangeRecord, UserEvent, Task,\
    Finance, Press, UserTask, Information, MAdvert_App,UserWelfare
from datetime import datetime, date, timedelta
from django.http.response import JsonResponse
from account.models import Userlogin, MyUser, UserSignIn
from .tools import app_login_required, user_info, is_authenticated_app
import hashlib
import time
from account.models import UserToken
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from account.transaction import charge_score, charge_money
from account.varify import verifymobilecode
from django.contrib.contenttypes.models import ContentType
from app.tools import is_authenticated_app
from wafuli.tools import saveImgAndGenerateUrl, update_view_count
from django.db import transaction
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Sum,Q,F
from wafuli_admin.models import DayStatis, GlobalStatis, RecommendRank

host = 'http://test.wafuli.cn'
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
            'type':wel.type,
        }
        ret_list.append(attr_dic)
    logger.debug(str(len(ret_list)))
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
    rlist = range(1,4)
    ret_list = []
    for i in rlist:
        adv_today = MAdvert_App.objects.filter(location=str(i),is_hidden=False).first()
        if adv_today:
            wel = adv_today.wel_id
            image = host + adv_today.pic.url
            location = i
            ret_list.append({
                'id':adv_today.id,
                'wel_id':wel.id,
                'image':image,
                'type':wel.type,
                'location': location,
                'title':wel.title     
            })
    return JsonResponse({'code':0,'data':ret_list})

def get_today_num(request):
    try:
        statis = DayStatis.objects.get(date=date.today())
    except:
        new_wel_num = 0
    else:
        new_wel_num = statis.new_wel_num
    glo_statis = GlobalStatis.objects.first()
    if glo_statis:
        all_wel_num = glo_statis.all_wel_num
    else:
        withdraw_total = 0
        all_wel_num = 0
    return JsonResponse({'code':0, 'new_num':new_wel_num, 'all_num':all_wel_num})

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

def get_content_task(request):
    ret_dict = {}
    id = request.GET.get("id")
    id = int(id)
    news = None
    try:
        news = Task.objects.get(id=id)
    except Task.DoesNotExist:
        ret_dict['code'] = 1
        ret_dict['msg'] = u"该任务不存在"
    else:
        ret_dict['code'] = 0
        strategy = news.strategy.replace('"/media/', '"' + host + '/media/')
        rules = news.rules.replace('"/media/', '"' + host + '/media/')
        taskinfo = {
            'is_forbidden': news.is_forbidden,
            'left_num':news.left_num,
            'rules':rules,
            'strategy':strategy,
            'url': news.exp_url if not news.isonMobile else (host + news.exp_code.url),
            'title':news.title,
            'ismobile': news.isonMobile,
        }
        ret_dict['taskinfo'] = taskinfo
        if is_authenticated_app(request):
            try:
                UserTask.objects.get(user=request.user,task=news)
            except UserTask.DoesNotExist:
                ret_dict.update(accepted=0)
            else:
                ret_dict.update(accepted=1)
    return JsonResponse(ret_dict)

@app_login_required
def get_user_task_state(request):
    ret = {}
    id = request.GET.get("id")
    id = int(id)
    news = None
    try:
        news = Task.objects.get(id=id)
    except Task.DoesNotExist:
        ret['code'] = 1
        ret['msg'] = u"该任务不存在"
    else:
        ret['code'] = 0
    try:
        UserTask.objects.get(user=request.user,task=news)
    except UserTask.DoesNotExist:
        ret.update(accepted=0)
    else:
        ret.update(accepted=1)
    return JsonResponse(ret)
@app_login_required
def accept_task(request):
    ret = {}
    id = request.GET.get("id")
    id = int(id)
    news = None
    wel_id = request.GET.get('id', None)
    if not wel_id:
        logger.error("wel_id is missing!!!")
        ret['code'] = 1
        ret['msg'] = u"该任务不存在"
        return JsonResponse(ret)
    wel_id = int(wel_id)
    wel = Task.objects.get(id=wel_id)
    if wel.left_num <= 0:
        ret['code'] = 2
        ret['msg'] = u"已经被抢光啦~"
    elif wel.is_forbidden:
        ret['code'] = 3
        ret['msg'] = u"数据统计中，暂停领取"
    else:
        obj, created = UserTask.objects.get_or_create(user=request.user, task=wel)
        if created:
            if wel.left_num <=1:
                wel.state = '2'
            wel.left_num = F("left_num")-1
            wel.save(update_fields=["left_num","state"])
        ret['code'] = 0
    return JsonResponse(ret)


@csrf_exempt
@app_login_required
def submit_task(request):
    news_id = request.POST.get('id', None)
    telnum = request.POST.get('telnum', '').strip()
    remark = request.POST.get('remark', '')
    if not (news_id and telnum):
        result = {'code':1, 'msg':u"请先领取任务再提交！"}
        return JsonResponse(result)
    news = Task.objects.get(pk=news_id)
    try:
        record = UserTask.objects.get(user=request.user,task=news)
    except UserTask.DoesNotExist:
        result = {'code':3, 'msg':u"请先领取任务再提交！"}
        return JsonResponse(result)
    is_futou = news.is_futou
    info_str = "news_id:" + news_id + "| invest_account:" + telnum + "| is_futou:" + str(is_futou)
    logger.info(info_str)
    code = None
    msg = ''
    userlog = None
    if is_futou:
        remark = u"复投：" + remark
    try:
        with transaction.atomic():
            if not is_futou and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
                raise ValueError('This invest_account is repective in project:' + str(news.id))
            else:
                userlog = UserEvent.objects.create(user=request.user, event_type='1', invest_account=telnum,
                                 invest_image='', content_object=news, audit_state='1',remark=remark,)
                code = 0
                msg = u'提交成功，请通过用户中心查询！'
    except Exception, e:
        logger.info(e)
        result = {'code':2, 'msg':u"该注册手机号已被提交过，请不要重复提交！"}
        return JsonResponse(result)
    else:
        imgurl_list = []
        if len(request.FILES)>6:
            result = {'code':4, 'msg':u"上传图片数量不能超过6张"}
            userlog.delete()
            return JsonResponse(result)
        for key in request.FILES:
            block = request.FILES[key]
            if block.size > 100*1024:
                result = {'code':5, 'msg':u"每张图片大小不能超过100k，请重新上传"}
                userlog.delete()
                return JsonResponse(result)
        for key in request.FILES:
            block = request.FILES[key]
            imgurl = saveImgAndGenerateUrl(key, block)
            imgurl_list.append(imgurl)
        invest_image = ';'.join(imgurl_list)
        userlog.invest_image = invest_image
        userlog.save(update_fields=['invest_image'])
        record.delete()
    result = {'code':code, 'msg':msg}
    return JsonResponse(result)

def get_content_finance(request):
    ret_dict = {}
    id = request.GET.get("id")
    id = int(id)
    news = None
    try:
        news = Finance.objects.get(id=id)
    except Finance.DoesNotExist:
        ret_dict['code'] = 1
        ret_dict['msg'] = u"该福利不存在"
    else:
        ret_dict['code'] = 0
        strategy = news.strategy.replace('"/media/', '"' + host + '/media/')
        rules = news.rules.replace('"/media/', '"' + host + '/media/')
        financeinfo = {
            'rules':rules,
            'strategy':strategy,
            'url': news.exp_url if not news.isonMobile else (host + news.exp_code.url),
            'title':news.title,
            'ismobile': news.isonMobile,
            'state': news.state
        }
        ret_dict['financeinfo'] = financeinfo
    return JsonResponse(ret_dict)

def get_content_information(request):
    ret_dict = {}
    id = request.GET.get("id")
    id = int(id)
    news = None
    try:
        news = Information.objects.get(id=id)
    except Information.DoesNotExist:
        ret_dict['code'] = 1
        ret_dict['msg'] = u"该新闻不存在"
    else:
        ret_dict['code'] = 0
        content = news.content.replace('"/media/', '"' + host + '/media/')
        info = {
            'source':news.source,
            'content':content,
            'time': news.pub_date.strftime("%Y-%m-%d %H:%M"),
        }
        ret_dict['info'] = info
    return JsonResponse(ret_dict)

@app_login_required
@csrf_exempt
def submit_finance(request):
    ret = {}
    news_id = request.POST.get('id', None)
    telnum = request.POST.get('telnum', '').strip()
    remark = request.POST.get('remark', '')
    term = request.POST.get('term', '').strip()
    amount = request.POST.get('amount',0)
    amount = Decimal(amount)
    if not (news_id and telnum):
        logger.error("news_id or telnum is missing!!!")
        ret['code'] = 1
        ret['msg'] = u"参数错误"
        return JsonResponse(ret)
    if len(telnum)>11 or len(remark)>200:
        ret['code'] = 3
        ret['msg'] = u"账号或备注过长"
        return JsonResponse(ret)
    news = None
#     if news.state != '1':
#         code = '4'
#         msg = u'该项目已结束或未开始！'
#         result = {'code':code, 'msg':msg}
#         return JsonResponse(result)
    news = Finance.objects.get(pk=news_id)
    is_futou = news.is_futou
    info_str = "news_id:" + news_id + "| invest_account:" + telnum + "| is_futou:" + str(is_futou)
    logger.info(info_str)
    if is_futou:
        remark = u"复投：" + remark
    try:
        with transaction.atomic():
            if not is_futou and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
                raise ValueError('This invest_account is repective in project:' + str(news.id))
            else:
                UserEvent.objects.create(user=request.user, event_type='1', invest_account=telnum, invest_term=term,
                                 invest_amount=amount, content_object=news, audit_state='1',remark=remark,)
                ret['code'] = 0
    except Exception, e:
        logger.info(e)
        ret['code'] = '2'
        ret['msg'] = u'该注册手机号已被提交过，请不要重复提交！'
    return JsonResponse(ret)


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
            info = user_info(user)
            result.update(info=info)
        return JsonResponse(result)


@app_login_required
@csrf_exempt
def get_user_info(request):
    user = request.user
    info = user_info(user)
    result = {'code':0}
    result.update(info=info)
    return JsonResponse(result)

@app_login_required
def charge_json(request):
    user = request.user
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get('type', '0'))
    start = 6*count
    item_list = TransList.objects.filter(user=user, transType=type)[start:start+6]
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

@app_login_required
def score_json(request):
    user = request.user
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get('type', '0'))
    start = 6*count
    item_list = ScoreTranlist.objects.filter(user=user, transType=type)[start:start+6]
    data = []
    for con in item_list:      
        i = {"reason":con.reason,
             "amount":con.transAmount,
             "date":con.time.strftime("%Y-%m-%d"),
             }
        if type == '1':
            event = con.user_event
            if event and event.event_type == '3':
                state = event.get_audit_state_display()
            else:
                state = u"无"
            i.update({"state":state})
        data.append(i)
    return JsonResponse(data, safe=False)

@app_login_required
def submit_order(request):
    result={'code':0, 'url':''}
    name = request.GET.get("name", '')
    tel = request.GET.get("tel", '')
    addr = request.GET.get("addr", '')
    remark= request.GET.get("remark", '')
    good_id= request.GET.get("id", '')
    good_id = int(good_id)
    commodity = Commodity.objects.get(pk=good_id)
    ret = charge_score(request.user, '1', commodity.price, commodity.name)
    if ret is not None:
        logger.debug('Exchanging scores is successfully reduced!')
        exg_obj = ExchangeRecord.objects.create(tranlist=ret,commodity=commodity,
                                      name=name,tel=tel,addr=addr,message=remark)
        event = UserEvent.objects.create(user=request.user, event_type='3',invest_amount=commodity.price,
                         audit_state='1',remark=remark, content_object=exg_obj)
        ret.user_event = event
        ret.save(update_fields=['user_event'])
        result['code'] = 0
    else:
        logger.debug('Exchanging scores is failed to reduce!!!')
        result['code'] = 1
    return JsonResponse(result)

@csrf_exempt
@app_login_required
def withdraw(request):
    user = request.user
    result = {'code':-1, 'msg':''}
    withdraw_amount = request.POST.get("amount", None)
    if not withdraw_amount:
        result['code'] = 3
        result['msg'] = u'传入参数不足！'
        return JsonResponse(result)
    try:
        withdraw_amount = int(withdraw_amount)
    except ValueError:
        result['code'] = -1
        result['msg'] = u'参数不合法！'
        return JsonResponse(result)
    if withdraw_amount < 1000 or withdraw_amount > user.balance:
        result['code'] = -1
        result['msg'] = u'余额不足！'
        return JsonResponse(result)
    if not user.zhifubao or not user.zhifubao_name:
        result['code'] = -1
        result['msg'] = u'请先绑定支付宝！'
    else:
        translist = charge_money(user, '1', withdraw_amount, u'提现')
        if translist:
            event = UserEvent.objects.create(user=user, event_type='2', invest_account=user.zhifubao,
                        invest_amount=withdraw_amount, audit_state='1')
            translist.user_event = event
            translist.save(update_fields=['user_event'])
            result['code'] = 0
            result['msg'] = u'提交成功，请耐心等待审核通过！'
        else:
            result['code'] = -2
            result['msg'] = u'提交失败！'
    return JsonResponse(result)

@app_login_required
def bind_zhifubao(request):
    result={}
    user = request.user
    zhifubao = request.POST.get("account", '')
    zhifubao_name = request.POST.get("name", '')
    if not user.zhifubao:
        user.zhifubao = zhifubao
        user.zhifubao_name = zhifubao_name
        user.save(update_fields=["zhifubao","zhifubao_name",])
        result['code'] = 0
        result['msg'] = u'绑定成功！'
    else:
       result['code'] = 3 
       result['msg'] = u'您已绑定过支付宝！'
    return JsonResponse(result)

@csrf_exempt
@app_login_required
def change_zhifubao(request):
    result={}
    user = request.user
    zhifubao = request.POST.get("account", '')
    zhifubao_name = request.POST.get("name", '')
    telcode = request.POST.get("telcode", '')
    ret = verifymobilecode(user.mobile,telcode)
    if ret != 0:
        result['code'] = 2
        if ret == -1:
            result['msg'] = u'请先获取手机验证码！'
        elif ret == 1:
            result['msg'] = u'手机验证码输入错误！'
        elif ret == 2:
            result['msg'] = u'手机验证码已过期，请重新获取'
        return JsonResponse(result)
    else:
        user.zhifubao = zhifubao
        user.zhifubao_name = zhifubao_name
        user.save(update_fields=["zhifubao","zhifubao_name",])
        result['code'] = 0
        result['msg'] = u"支付宝账号更改成功！"
    return JsonResponse(result)

@csrf_exempt
@app_login_required
def password_change(request):
    result={}
    init_password = request.POST.get("initp", '')
    new_password = request.POST.get("newp", '')
    if not (init_password and new_password):
        result['code'] = 1
        result['msg'] = u'请输入密码！'
        return JsonResponse(result)
    user = request.user
    if not user.check_password(init_password):
        result['code'] = 2
        result['msg'] = u'当前密码输入错误！'
    else:
        user.set_password(new_password)
        user.save(update_fields=["password"])
        result['code'] = 0
        result['msg'] = u'密码修改成功！'
    return JsonResponse(result)

@csrf_exempt
@app_login_required
def invite_to_balance(request):
    inviter = request.user
    left_award = inviter.invite_account
    result = {}
    if left_award == 0:
        result['code'] = 1
        result['msg'] = u'邀请奖励结余为0'
    else:
        translist = charge_money(inviter, '0', left_award, u'邀请奖励')
        if translist:
            inviter.invite_account = 0
            inviter.save(update_fields=['invite_account'])
            event = UserEvent.objects.create(user=inviter, event_type='5',
                        invest_amount=left_award, audit_state='1')
            translist.user_event = event
            translist.save(update_fields=['user_event'])
            result['code'] = 0
        else:
            result['code'] = 2
            result['msg'] = u'操作失败，请联系客服！'
    return JsonResponse(result)


@app_login_required
@csrf_exempt
def get_invite_info(request):
    inviter = request.user
    withdraw_thismonth = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                audit_state='0',audit_time__year=time.localtime()[0],audit_time__month=time.localtime()[1]).\
                aggregate(sumofwith=Sum('invest_amount'))
    acc_count = inviter.invitees.count()
    acc_with_count = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                audit_state='0').values('user__mobile').distinct().order_by().count()
    this_month_award = float(withdraw_thismonth.get('sumofwith') or 0)*settings.AWARD_RATE
    this_month_award = int(this_month_award)
    statis = {
        'code':0,
        'left_award':inviter.invite_account,
        'accu_invite_award':inviter.invite_income,   
        'accu_invite_scores':inviter.invite_scores,
        'acc_count':acc_count,
        'acc_with_count':acc_with_count,
        'this_month_award':this_month_award, 
    }
    return JsonResponse(statis)

def strategy(request):
    item_list = Press.objects
    strategy_list = item_list.filter(type='2')
    notice_list = item_list.filter(type='1')
    slist = []
    for s in strategy_list:
        slist.append({'id':s.id, 'title':s.title})
    nlist = []
    for n in notice_list:
        nlist.append({'id':n.id, 'title':n.title})
    return JsonResponse({'slist':slist,'nlist':nlist})

def get_content_press(request):
    id = request.GET.get('id')
    press = None
    press = Press.objects.get(id=id)
    strategy = press.content
    strategy = strategy.replace('"/media/', '"' + host + '/media/')
    return JsonResponse({'content':strategy})

@app_login_required
def signin(request):
    result = {}
    today = date.today()
    signin_last = UserSignIn.objects.filter(user=request.user).first()
    if signin_last and signin_last.date == today:
        result['code'] = 1
    else:
        signed_conse_days = 1
        if signin_last and signin_last.date == today - timedelta(days=1):
            signed_conse_days += signin_last.signed_conse_days
        UserSignIn.objects.create(user=request.user, date=date.today(), signed_conse_days=signed_conse_days)
        charge_score(request.user, '0', 5, u"签到奖励")
        if signed_conse_days%7 == 0:
            charge_score(request.user, '0', 20, u"连续签到7天奖励")
        result['code'] = 0
    first_day_of_month = today - timedelta(today.day-1)
    sign_days = UserSignIn.objects.filter(user=request.user,date__gte=first_day_of_month).values('date');
    records = []
    for day in sign_days:
        records.append(day.get('date').day);
    result['records'] = records
#     result.update(scores=request.user.scores, userimg=request.user.id%4)
    return JsonResponse(result)

@csrf_exempt
@app_login_required
def recom_submit(request):
    user = request.user
    result = {}
    sumbit_num_today = UserWelfare.objects.filter(user=user, date__gte=datetime.date.today()).count()
    if sumbit_num_today>=5:
        result['code'] = 4
        result['msg'] = u'每天最多只能提交5条哦，请明日再来！'
        return JsonResponse(result)
    title = request.POST.get('title', '')
    url = request.POST.get('url', '')
    reason = request.POST.get('reason', '')
    if not (title and url) or len(title)>200 or len(url)>200 or len(reason)>200:
        result['code'] = 3
        result['msg'] = u'输入参数长度有误！'
    else:
        try:
            wel = UserWelfare.objects.create(user=user, title=title,url=url,reason=reason)
            UserEvent.objects.create(user=user, event_type='6', content_object=wel, audit_state='1')
        except Exception as e:
            result['code'] = 2
            result['msg'] = u'重复提交或数据有误！'
            logger.warning(e)
        else:
            result['code'] = 0
            result['msg'] = u'提交成功！'
    return JsonResponse(result)


def recom_rank(request):
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

@app_login_required
def recom_info(request):
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
