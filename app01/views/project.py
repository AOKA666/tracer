import time
from django.shortcuts import render, redirect
from app01.forms.project import ProjectForm
from django.http import JsonResponse
from app01 import models
from app01.utils.tencent.cos import create_bucket


def project_list(request):
    if request.method == 'GET':
        form = ProjectForm(request)
        # 存放所有项目用于前端显示
        project_display = {"star": [], "join": [], "create": []}
        # 我创建的
        all_projects = models.Project.objects.filter(creator=request.tracer)
        for project in all_projects:
            if project.star:
                project_display['star'].append({"project": project, "project_type": "my"})
            else:
                project_display['create'].append(project)
        # 我参与的
        join_projects = models.ProjectUser.objects.filter(user=request.tracer)
        for project in join_projects:
            if project.start:
                project_display['star'].append({"project": project, "project_type": "join"})
            else:
                project_display['join'].append(project)
        return render(request, 'app01/project_list.html', {'form': form, 'project_display': project_display})
    form = ProjectForm(request, request.POST)
    if form.is_valid():
        # 创建桶
        bucket = "{}-{}-1307733527".format(request.POST.get("name"), str(int(time.time())))
        create_bucket(bucket_name=bucket)
        form.instance.creator = request.tracer
        form.instance.bucket = bucket
        instance = form.save()
        # 初始化问题类型
        issue_type_list = []
        for item in models.IssueType.default_type:
            issue_type_list.append(models.IssueType(title=item, project=instance))
        models.IssueType.objects.bulk_create(issue_type_list)
        return JsonResponse({"status": 1})
    return JsonResponse({"status": 0, "msg": form.errors})


def star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer).update(star=True)
    elif project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer).update(star=True)
    return redirect('app01:project_list')


def cancel_star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer).update(star=False)
    elif project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer).update(star=False)
    return redirect('app01:project_list')
