from django.shortcuts import render
from django.db.models import Count
from django.urls import reverse
from app01 import models


def dashboard(request, project_id):
    # 问题
    default_issue_list = models.Issue.status_choices
    issue_dict = {}
    for item in default_issue_list:
        issue_dict[item[0]] = {"type": item[1], "count": 0}
    issue_list = models.Issue.objects.filter(project_id=project_id).values("status").annotate(c=Count("id"))
    for obj in issue_list:
        issue_dict[obj['status']]['count'] = obj['c']
    return render(request, 'app01/dashboard.html', {"issue_dict": issue_dict})