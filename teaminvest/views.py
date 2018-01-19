from django.shortcuts import render
from teaminvest.models import Project
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def teaminvest_submit(request):
    projects = Project.objects.filter(state='10')
    return render(request, 'm_teaminvest_submit.html', {'projects':projects})