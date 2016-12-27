from django.shortcuts import render
import hashlib
from django.http.response import HttpResponse,Http404
import logging
logger = logging.getLogger('wafuli')
def weixin(request):
    token = '1hblsqTsdfsdfsd'
    timestamp = str(request.GET.get('timestamp'))
    nonce = str(request.GET.get('nonce'))
    signature = str(request.GET.get('signature'))
    echostr = str(request.GET.get('echostr'))
    paralist = [token,timestamp,nonce]
    paralist.sort()
    parastr = ''.join(paralist)
    siggen = hashlib.sha1(parastr).hexdigest()
    logger.info(siggen)
    logger.info(signature) 
    if siggen==signature:
        return HttpResponse(echostr)
    else:
        raise Http404

def bind_user(request):
    return render(request, 'm_login.html')