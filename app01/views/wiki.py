from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from app01.forms.wiki import WikiForm
from app01 import models
from app01.utils.tencent.cos import cos_upload_file
from app01.utils.common import uid
from django.views.decorators.clickjacking import xframe_options_exempt


def wiki(request, project_id):
    """点击wiki显示页面的视图函数"""
    wiki_id = request.GET.get("id")
    if not wiki_id or not wiki_id.isdecimal():
        wiki_obj = None
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'app01/wiki.html', {"wiki_obj": wiki_obj})


def wiki_add(request, project_id):
    """添加wiki"""
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
        return redirect(reverse('app01:wiki', kwargs={"project_id": project_id}))


def wiki_list(request, project_id):
    wiki_list = models.Wiki.objects.filter(project_id=project_id).values(
        "id", "title", "parent_id"
    ).order_by('depth', 'id')
    return JsonResponse({"status": True, "data": list(wiki_list)})


def wiki_edit(request, project_id, wiki_id):
    wiki = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if request.method == 'POST':
        form = WikiForm(request, instance=wiki, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('app01:wiki', kwargs={"project_id": project_id}))
    else:
        form = WikiForm(request, instance=wiki)
    return render(request, "app01/wiki_add.html", {"form": form})


def wiki_delete(request, project_id, wiki_id):
    wiki = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if wiki:
        wiki.delete()
        return redirect(reverse('app01:wiki', kwargs={"project_id": project_id}))


@csrf_exempt
@xframe_options_exempt
def upload(request, project_id):
    result = {"success": 0, "message": None, "url": None}
    project = models.Project.objects.get(id=project_id)
    img = request.FILES.get('editormd-image-file')
    if not img:
        result["message"] = "文件不存在"
        return JsonResponse(result)
    # 获取文件后缀
    ext = img.name.rsplit('.')[-1]
    # 自定义生成文件名
    key = uid(str(request.tracer.phone))
    file_name = "{}.{}".format(key, ext)
    img_url = cos_upload_file(project.bucket, img, file_name)
    result["success"] = 1
    result["url"] = img_url
    print(result)
    return JsonResponse(result)
