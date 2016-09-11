from django.http.response import Http404
from django.http import JsonResponse
from wafuli.models import Welfare, Task, Finance, Information
# Create your views here.
import logging
logger = logging.getLogger('wafuli')
def update(request):
    if not request.is_ajax():
        raise Http404
    result = {'code':1 }
    news_id = request.GET.get('id', None)
    news_type = request.GET.get('type', None)
    if news_id and news_type:
        try:
            model = globals()[news_type]
            news = model.objects.get(id=news_id)
            news.view_count += 1
            news.save(update_fields=['view_count',])
            if hasattr(news, 'company'):
                company = news.company
                if company:
                    company.view_count += 1
                    company.save(update_fields=['view_count',])
            result['code'] = 0
        except Exception as e:
            logger.error(e)
            pass;
    
    return JsonResponse(result)