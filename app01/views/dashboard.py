from django.shortcuts import render
from django.db.models import Count
from django.urls import reverse
from app01 import models


def dashboard(request, project_id):
    # 问题
    default_issue_list = models.Issue.status_choices
    issue_dict = {}
    color_list = ["red","blue","green","yellow","purple","orange","brown"]
    for item in default_issue_list:
        issue_dict[item[0]] = {"type": item[1], "count": 0, "color": color_list[default_issue_list.index(item)]}
    issue_list = models.Issue.objects.filter(project_id=project_id).values("status").annotate(c=Count("id"))
    for obj in issue_list:
        issue_dict[obj['status']]['count'] = obj['c']
    # 动态
    activity = models.Issue.objects.filter(assign__isnull=False).order_by("-create_time")[0:10]
    print(activity)
    return render(request, 'app01/dashboard.html', {"issue_dict": issue_dict, "activity": activity})