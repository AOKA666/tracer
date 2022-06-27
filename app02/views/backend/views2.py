from django.http import JsonResponse
from django.shortcuts import render
from app02 import models


def backend(request):
    return render(request, 'backend/app02/main.html')


def create_project(request):
    if request.method == 'POST':
        ret = {"status":1, "message":""}
        started = request.tracer.project_set.all().count()
        limit = request.tracer.transaction_set.all().last().price.project_num_count        
        if started < limit:
            print(started, limit)
            # name = request.POST.get("title")
            # color = request.POST.get("color")
            # dis = request.POST.get("des")
            # models.Project.objects.create(
            #     name=name,
            #     distract=dis,
            #     color=color,

            # )
        else:
            ret["status"] = 0
            ret["message"] = "已超过可创建项目上限！"
        return JsonResponse(ret)