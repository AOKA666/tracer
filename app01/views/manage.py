from django.shortcuts import render
from app01 import models


def dashboard(request, project_id):
    return render(request, 'app01/dashboard.html')


def issues(request, project_id):
    return render(request, 'app01/issues.html')


def statistics(request, project_id):
    return render(request, 'app01/statistics.html')


def file(request, project_id):
    return render(request, 'app01/file.html')


def settings(request, project_id):
    return render(request, 'app01/settings.html')