#coding:utf-8
'''
Created on 20161116

@author: lch
'''
import functools
import time
from account.models import UserToken
from django.http.response import JsonResponse
from account.models import MyUser
from django.contrib.contenttypes.models import ContentType
from wafuli.models import UserEvent, Task, Finance
from account.tools import logger


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
            logger.error(str(token));
            if expire < now:
                logger.error("asdfggdddddddddddddddddd");
                return False
            else:
                request.user = token.user
        except:
            logger.error("asdfggggggggggggggggggggggggg");
            return False
        else:
            return True

def user_info(user):
    ttype = ContentType.objects.get_for_model(Task)
    ftype = ContentType.objects.get_for_model(Finance)
    tcount_u = UserEvent.objects.filter(user=user, content_type = ttype.id).count()
    fcount_u = UserEvent.objects.filter(user=user, content_type = ftype.id).count()
    result = {'accu_income':user.accu_income, 'balance':user.balance, 
              'mobile':user.mobile, 'userimg':user.id%4, 'scores':user.scores,
              'accu_scores':user.accu_scores, 'zhifubao':user.zhifubao, 'tcount_u':tcount_u,
              'fcount_u':fcount_u,'invite_code':user.invite_code}
    return result