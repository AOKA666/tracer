import datetime
from collections import OrderedDict
from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from app01 import models


def statistics(request, project_id):
    return render(request, 'app01/statistics.html')


def get_status(request, project_id):
    """
    每个项目下分派的人员任务完成情况

    最终构建的数据形式
    [{
        name: '新建',
        data: [1, 1, ],
    }, {
        name: '待处理',
        data: [1, 0, ],
    }]

    首次构建的数据形式
    "1":{
        "name": "WCY",
        "data":{
            "新建":2,
            "进行中":3,
            ...
        }
    }
    "2":{
        "name": "BBY",
        "data":{
            "新建":3,
            "进行中":2,
            ...
        }
    }
    """
    start = request.GET.get("start")
    end = request.GET.get("end")
    # 处理日期，此处应该加一天
    end = datetime.datetime.strptime(end, "%Y-%m-%d")+datetime.timedelta(hours=23,minutes=59,seconds=59)
    user_list = models.Issue.objects.filter(project_id=project_id).values_list("assign").distinct()
    assign_dict = OrderedDict()
    for user in user_list:
        assign_dict[user[0]] = {
            "name": user[0],
            "data": {i[0]: 0 for i in models.Issue.status_choices}
            }
    # print(assign_dict)
    # {3: {'name': 3, 'data': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}, None: {'name': None, 'data': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}}
    issue_list = models.Issue.objects.filter(project_id=project_id, create_time__lt=end, create_time__gte=start).values("assign", "status").annotate(count=Count("id"))
    # print(issue_list)
    # <QuerySet [{'assign': None, 'status': 1, 'count': 1}, {'assign': 3, 'status': 1, 'count': 1}, {'assign': 3, 'status': 2, 'count': 1}, {'assign': 3, 'status': 5, 'count': 1}]>
    for issue in issue_list:
        assign_dict[issue["assign"]]["data"][issue["status"]] = issue["count"]
    # print(assign_dict)
    # {3: {'name': 3, 'data': {1: 1, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0}}, None: {'name': None, 'data': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}}
    result = []
    for item in models.Issue.status_choices:
        result.append({"name": item[1], "data":[data["data"][item[0]] for data in assign_dict.values()]})
    # print(result)
    # [{'name': '新建', 'data': [1, 1]}, {'name': '处理中', 'data': [1, 0]}, {'name': '已解决', 'data': [0, 0]}, ...]
    ls = list(assign_dict.keys())
    categories = []
    for i in ls:
        if i:
            categories.append(models.UserInfo.objects.get(id=i).username)
        else:
            categories.append("未指派")
    return JsonResponse({"categories": categories, "series":result})


def get_priority(request, project_id):
    start = request.GET.get("start")
    end = request.GET.get("end")
    end = datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(hours=23, minutes=59, seconds=59)
    issue_list = models.Issue.objects.filter(project_id=project_id, create_time__lt=end, create_time__gte=start).values("priority").annotate(count=Count("id"))
    tpl = {"danger": "高", "warning": "中", "success": "低"}
    ret = {}
    for i in list(issue_list):
        ret[tpl[i['priority']]] = i['count']
    return JsonResponse(ret)