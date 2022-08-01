from django.shortcuts import render
from app01 import models


def dashboard(request, project_id):
    return render(request, 'app01/dashboard.html')


def statistics(request, project_id):
    return render(request, 'app01/statistics.html')
