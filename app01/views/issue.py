import json

from django .shortcuts import render
from app01.forms.issues import IssueForm, IssueRecordForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from app01 import models


def issues(request, project_id):
    if request.method == 'GET':
        issue_list = models.Issue.objects.all().order_by("-id")
        # 分页
        paginator = Paginator(issue_list, per_page=2)
        current_page = request.GET.get("page", "1")
        if not current_page.isdecimal():
            current_page = 1
        if int(current_page) > paginator.num_pages or int(current_page) < 0:
            current_page = int(paginator.num_pages)
        else:
            current_page = int(current_page)
        query_set = paginator.page(current_page)
        form = IssueForm(request)
        return render(request, 'app01/issues.html', locals())
    form = IssueForm(request, data=request.POST)
    if form.is_valid():
        result_dict = form.cleaned_data
        result_dict.update({"project_id": project_id, "creator": request.tracer})
        form.instance.project_id = project_id
        form.instance.creator = request.tracer
        form.save()
        return JsonResponse({"status": True})
    else:
        return JsonResponse({"status": False, "data": form.errors})


def details(request, project_id, issue_id):
    issue_obj = models.Issue.objects.filter(id=issue_id, project_id=project_id).first()
    form = IssueForm(request, instance=issue_obj)
    return render(request, 'app01/issue_details.html', {"form": form, "issue_obj": issue_obj})


@csrf_exempt
def record(request, project_id, issue_id):
    if request.method == 'GET':
        reply_list = models.IssueReply.objects.filter(issue_id=issue_id).order_by("depth", "-time").values(
            "id", "content", "parent_id", "creator__username", "time", "type")
        result = list(reply_list)
        # 更改时间格式
        for each in result:
            each['time'] = each['time'].strftime("%Y-%m-%d %H:%M:%S")
        return JsonResponse({"data": result})
    form = IssueRecordForm(request.POST)
    if form.is_valid():
        form.instance.issue_id = issue_id
        form.instance.creator = request.tracer
        parent_id = request.POST.get("parent")
        if parent_id:
            form.instance.depth = models.IssueReply.objects.get(id=parent_id).depth + 1
        else:
            form.instance.depth = 1
        instance = form.save()
        result_dict = [{
            "id": instance.id,
            "content": instance.content,
            "parent_id": instance.parent_id,
            "creator__username": instance.creator.username,
            "time": instance.time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": instance.type
        }]
        return JsonResponse({"status": True, "data": result_dict})
    else:
        return JsonResponse({"status": False, "errors": form.errors})


@csrf_exempt
def data_change(request, project_id, issue_id):
    data_dict = json.loads(request.body.decode("utf-8"))
    print(data_dict)
    issue_obj = models.Issue.objects.filter(id=issue_id, project_id=project_id).first()
    """
    判断数据来源
        1. 输入框：subject, content, start_time, end_time
        2. 下拉框：type, module, mode, status, priority
        3. 外键：parent, assign
        4. 多对多：attention
    """
    name = data_dict.get("name")
    value = data_dict.get("value")
    field = models.Issue._meta.get_field(name)
    if name in ["subject", "content", "start_time", "end_time"]:
        if not value:
            # 是否允许为空
            if not field.null:
                return JsonResponse({"status": False, "msg": "该字段不能为空"})
            else:
                setattr(issue_obj, name, value)
                issue_obj.save()
    return JsonResponse({})