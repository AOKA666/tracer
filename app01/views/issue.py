from django .shortcuts import render
from app01.forms.issues import IssueForm
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from app01 import models


def issues(request, project_id):
    if request.method == 'GET':
        issue_list = models.Issue.objects.all()
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
        print(query_set)
        for i in query_set:
            print(i)
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
    reply_list = models.IssueReply.objects.filter(project_id=project_id, issue_id=issue_id).values_list(
        "id", "title", "content", "parent_id")
    print(reply_list)
    return render(request, 'app01/issue_details.html', {"form": form, "reply_list": reply_list})