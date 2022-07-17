from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from app01 import models
from app01.forms.file import FileRepositoryForm


def file(request, project_id):
    if request.method == 'GET':
        file_list = models.FileRepository.objects.filter(project_id=project_id, parent=None)
        form = FileRepositoryForm()
        return render(request, 'app01/file.html', {"file_list": file_list, "form": form})
    form = FileRepositoryForm(request.POST)
    ret = {"status": 1, "msg": ""}
    if form.is_valid():
        form.instance.update_user = request.tracer
        form.save()


