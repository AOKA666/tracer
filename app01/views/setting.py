from django.shortcuts import render, redirect
from django.urls import reverse
from app01 import models
from app01.utils.tencent.cos import delete_bucket


def settings(request, project_id):
    return render(request, 'app01/settings.html')


def project_delete(request, project_id):
    """删除项目"""
    if request.method == 'GET':
        return render(request, 'app01/project_delete.html', {"error": ""})
    project_name = request.POST.get("project_name")
    print(project_name)
    if not project_name or project_name != request.project.name:
        return render(request, 'app01/project_delete.html', {"error": "项目名错误"})
    elif request.tracer != request.project.creator:
        return render(request, 'app01/project_delete.html', {"error": "只有项目创建者才可以删除项目"})
    bucket_name = models.Project.objects.filter(name=project_name).first().bucket
    # 删除桶
    delete_bucket(bucket_name)
    models.Project.objects.filter(name=project_name).delete()
    return redirect(reverse('app01:dashboard', kwargs={"project_id":project_id}))

    
