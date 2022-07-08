from django.shortcuts import render
from app01.forms.project import ProjectForm
from django.http import JsonResponse
from app01 import models


def project_list(request):
    if request.method == 'GET':
        form = ProjectForm(request)
        # 存放所有项目用于前端显示
        project_list = {"star":[], "join":[], "create":[]}
        # 我创建的
        all_projects = models.Project.objects.filter(creator=request.tracer)
        for project in all_projects:
            if project.start:
                project_list.star.append({"project": project, "project_id": project.id})
            else:
                project_list.create.append(project)
        # 我参与的
        join_projects = models.ProjectUser.objects.filter(user=request.tracer)
        for project in join_projects:
            if project.start:
                project_list.star.append({"project": project, "project_id": project.id})
            else:
                project_list.join.append(project)
        return render(request, 'app01/project_list.html', {'form': form, 'project_list': project_list})
    form = ProjectForm(request, request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer
        form.save()
        return JsonResponse({"status": 1})
    return JsonResponse({"status": 0, "msg": form.errors})
