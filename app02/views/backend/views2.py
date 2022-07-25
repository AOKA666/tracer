from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from app02 import models


def backend(request):
    create_project_list = models.Project.objects.filter(starter=request.tracer)
    invited_project_list = models.ProjectMember.objects.filter(user=request.tracer)
    return render(request, 'backend/app02/main.html', locals())


def create_project(request):
    if request.method == 'POST':
        ret = {"status": 1, "error": ""}
        name = request.POST.get("title")
        color = request.POST.get("color")
        dis = request.POST.get("des")
        models.Project.objects.create(
            name=name,
            distract=dis,
            color=color,
            starter=request.tracer,
            member_num=1,
            size=0
        )
        return JsonResponse(ret)


def eligibility(request):
    started = request.tracer.project_set.all().count()
    limit = request.tracer.transaction_set.all().last().price.project_num_count
    if started == limit:
        return HttpResponse(0)