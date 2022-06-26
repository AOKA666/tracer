from django.shortcuts import render
from app02 import models


def backend(request):
    return render(request, 'backend/app02/main.html')


def create_project(request):
    if request.method == 'POST':
        name = request.POST.get("title")
        color = request.POST.get("color")
        dis = request.POST.get("des")
        models.Project.objects.create(
            name=name,
            distract=dis,
            color=color,

        )