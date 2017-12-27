from django.shortcuts import render
from teaminvest.models import Project

# Create your views here.
def teaminvest_submit(request):
    projects = Project.objects.filter(state='10')
    return render(request, 'teaminvest_submit.html', {'projects':projects})