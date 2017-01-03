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
