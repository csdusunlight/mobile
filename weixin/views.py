from django.shortcuts import render
import hashlib
from django.http.response import HttpResponse,Http404
import logging
logger = logging.getLogger('wafuli')
def token_verify(request):
    token = 'Q5l1JNdTlyAlJ5evuJPE'
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    signature = request.GET.get('signature')
    echostr = request.GET.get('echostr') 
    paralist = [token,timestamp,nonce].sort()
    parastr = ''.join(paralist)
    siggen = hashlib.sha1(parastr).hexdigest()
    logger.info(siggen)
    logger.info(signature) 
    if siggen==signature:
        return HttpResponse(echostr)
    else:
        raise Http404
    