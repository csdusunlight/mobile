#coding:utf-8
'''
Created on 20161116

@author: lch
'''
import functools
import time
from account.models import UserToken, UserSignIn
from django.http.response import JsonResponse
from account.models import MyUser
from django.contrib.contenttypes.models import ContentType
from wafuli.models import UserEvent, Task, Finance
from datetime import datetime,date


def app_login_required(view):
    @functools.wraps(view)
    def decorator(request):
        ret = {}
        token = request.POST.get("token") or request.GET.get("token")
        if not token:
            ret.update(code=-1,msg='Token missing')
        else:
            try:
                now = int(time.time()*1000)
                token = UserToken.objects.get(token=token)
                expire = token.expire
                if expire < now:
                    ret.update(code=-3,msg='Token expired')
                else:
                    request.user = token.user
            except:
                ret.update(code=-2,msg='Invalid Token')
            else:
                return view(request)
        return JsonResponse(ret)
    return decorator

# def test(view):
#     @functools.wraps(view)
#     def decorator(request):
#         request.user = MyUser.objects.get(id=1)
#         return view(request)
#     return decorator

def is_authenticated_app(request):
    token = request.POST.get("token") or request.GET.get("token")
    if not token:
        return False
    else:
        try:
            now = int(time.time()*1000)
            token = UserToken.objects.get(token=token)
            expire = token.expire
            if expire < now:
                return False
            else:
                request.user = token.user
        except:
            return False
        else:
            return True

def user_info(user):
    ttype = ContentType.objects.get_for_model(Task)
    ftype = ContentType.objects.get_for_model(Finance)
    tcount_u = UserEvent.objects.filter(user=user, content_type = ttype.id).count()
    fcount_u = UserEvent.objects.filter(user=user, content_type = ftype.id).count()
    signin_last = UserSignIn.objects.filter(user=user).first()
    isSigned = 0
    if signin_last and signin_last.date == date.today():
        isSigned = 1
    isChannel = 1 if user.is_channel else 0
    bankcard = user.user_bankcard.first()
    card_number = bankcard.card_number if bankcard else ''
    bank = bankcard.bank if bankcard else ''
    bank_name = bankcard.get_bank_display() if bankcard else ''
    result = {'accu_income':user.accu_income, 'balance':user.balance, 'userid':user.id,
              'mobile':user.mobile, 'userimg':user.id%4, 'scores':user.scores,
              'accu_scores':user.accu_scores, 'card_number':card_number,'bank':bank,'tcount_u':tcount_u,
              'bank_name':bank_name, 'with_total':user.with_total, 'with_level':user.with_level, 'level':user.level,
              'fcount_u':fcount_u,'invite_code':user.invite_code,'isSigned':isSigned,'isChannel':isChannel}
    return result