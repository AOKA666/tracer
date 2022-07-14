from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from app01.forms.wiki import WikiForm
from app01 import models


def wiki(request, project_id):
    wiki_id = request.GET.get("id")
    if not wiki_id or not wiki_id.isdecimal():
        wiki_obj = None
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'app01/wiki.html', {"wiki_obj": wiki_obj})


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = WikiForm(request)
        return render(request, "app01/wiki_add.html", {"form": form})
    form = WikiForm(request, request.POST)
    if form.is_valid():
        form.instance.project_id = project_id
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        return redirect("app01:wiki", project_id=project_id)


def wiki_list(request, project_id):
    wiki_list = models.Wiki.objects.filter(project_id=project_id).values(
        "id", "title", "parent_id"
    ).order_by('depth', 'id')
    return JsonResponse({"status": True, "data": list(wiki_list)})


def wiki_edit(request, project_id, wiki_id):
    wiki = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    form = WikiForm(request, instance=wiki)
    return render(request, "app01/wiki_add.html", {"form": form})