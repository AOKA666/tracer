from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from app01 import models


def statistics(request, project_id):
    return render(request, 'app01/statistics.html')


def get_statistics(request, project_id):
    """
    [{
        name: '小张',
        data: [5, 3, 4, 7, 2],
        stack: 'male' // stack 值相同的为同一组
    }, {
        name: '小潘',
        data: [3, 4, 4, 2, 5],
        stack: 'male'
    }]
    """
    issue_list = models.Issue.objects.filter(project_id=project_id).values("status").annotate(c=Count("id"))
    print(issue_list)
    return JsonResponse({})