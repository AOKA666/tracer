import time
from collections import OrderedDict
import datetime
from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from app01 import models


def dashboard(request, project_id):
    # 问题
    default_issue_list = models.Issue.status_choices
    issue_dict = OrderedDict()
    color_list = ["red","blue","green","yellow","purple","orange","brown"]
    for item in default_issue_list:
        issue_dict[item[0]] = {"type": item[1], "count": 0, "color": color_list[default_issue_list.index(item)]}
    issue_list = models.Issue.objects.filter(project_id=project_id).values("status").annotate(c=Count("id"))
    for obj in issue_list:
        issue_dict[obj['status']]['count'] = obj['c']
    # 动态(显示10条)
    activity = models.Issue.objects.filter(assign__isnull=False).order_by("-create_time")[0:10]

    return render(request, 'app01/dashboard.html', {"issue_dict": issue_dict, "activity": activity})


def issue_trend(request, project_id):
    """新增问题趋势"""
    all_dates = {}
    for i in range(30):
        current_time = (datetime.date.today() - datetime.timedelta(days=(30 - i)))
        all_dates[current_time.strftime("%m-%d")] = [time.mktime(current_time.timetuple())*1000, 0]
    today = datetime.datetime.now().date()
    last_month = today - datetime.timedelta(days=30)
    new_issues = models.Issue.objects.filter(
        project_id=project_id, create_time__gte=last_month, create_time__lte=today).values("create_time").annotate(
        c=Count("id"))
    """
    方法2(sqlite): new_issues = models.Issue.objects.filter(
        project_id=project_id, create_time__gte=last_month, create_time__lte=today).extra(
            select={"ctime":"strftime('%%Y-%%m-%%d', app01_issue.create_time)"}
        ).values("create_time").annotate(
        c=Count("id"))
        
    方法3(mysql): new_issues = models.Issue.objects.filter(
        project_id=project_id, create_time__gte=last_month, create_time__lte=today).extra(
            select={"ctime":"DATE_FORMAT(app01_issue.create_time, '%%Y-%%m-%%d')"}
        ).values("create_time").annotate(
        c=Count("id"))
    """
    for item in new_issues:
        item['create_time'] = item['create_time'].strftime("%m-%d")
    for i in new_issues:
        all_dates[i['create_time']][1] += i['c']

    return JsonResponse({"data": list(all_dates.values())})
