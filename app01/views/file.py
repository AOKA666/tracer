import json
from urllib import response
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app01 import models
from app01.forms.file import FileRepositoryForm, EditFolderForm, UploadPostForm
from app01.utils.tencent.cos import get_credential


def file(request, project_id):
    parent_id = request.GET.get("folder", "")
    parent_obj = None
    if request.method == 'GET':
        # 导航条
        nav_list = []
        file_list = models.FileRepository.objects.filter(project_id=project_id)        
        if parent_id.isdecimal():
            parent = models.FileRepository.objects.filter(id=parent_id, project_id=project_id).first()
            parent_obj = parent
            while parent:
                nav_list.insert(0, {"id": parent.id, "name": parent.name})
                parent = parent.parent
            file_list = file_list.filter(parent_id=parent_id)
        else:
            file_list = file_list.filter(parent_id=None)
        form = FileRepositoryForm(request)
        back_dict = {
            "file_list": file_list,
            "form": form,
            "nav_list": nav_list,
            "parent_folder": parent_obj
        }
        return render(request, 'app01/file.html', back_dict)
    # post请求，添加或编辑
    fid = request.POST.get("fid","")
    ret = {"status": 1, "msg": ""}
    if fid.isdecimal():
        # 编辑
        file_obj = models.FileRepository.objects.filter(id=fid, project_id=project_id).first()
        form = EditFolderForm(instance=file_obj, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            ret["status"] = 0
            ret["msg"] = form.errors
        return JsonResponse(ret)
    else:
        # 添加
        form = FileRepositoryForm(request, data=request.POST)
        
        if form.is_valid():
            form.instance.project = request.project
            form.instance.type = 2
            form.instance.update_user = request.tracer
            form.instance.parent_id = parent_id
            form.save()
        else:
            ret["status"] = 0
            ret["msg"] = form.errors
        return JsonResponse(ret)


def delete(request, project_id):
    fid = request.GET.get("fid", "")
    used_space = request.project.use_space
    # 创建一个存储文件的列表
    file_list = []
    if fid.isdecimal():
        obj = models.FileRepository.objects.filter(id=fid, project_id=project_id).first()
        if obj.type == 1:
            # 是文件，放入列表中
            used_space -= obj.file_size
            file_list.append(obj)
        else:
            folder_list = [obj,]
            for item in folder_list:
                children_list = item.children.order_by("-type")
                # children_list为空也不会报错
                for child in children_list:
                    if child.type == '1':
                        file_list.append(child)
                        used_space -= child.file_size
                    else:
                        folder_list.append(child)
        # 循环完成之后列表中只剩下一个个文件
        models.FileRepository.objects.filter(id=fid, project_id=project_id).delete()
        # request.project.use_space.update(use_space=used_space)
        # request.project.save()
        return JsonResponse({"status": True})


@csrf_exempt
def cos_credential(request, project_id):
    """上传文件获取临时凭证"""
    data = json.loads(request.body.decode("utf-8"))
    print(data)
    # 已用空间容量
    used_space = request.project.use_space
    for item in data:
        used_space += item.get("size") 
    # 当前套餐空间容量限制
    limit = request.price_policy.price_policy.project_space * 1024 * 1024
    if used_space > limit:
        return JsonResponse({"status": False, "message": "已超出容量限制，请升级套餐！"})
    data = get_credential(request.project.bucket)
    data.update({"status": True})
    return JsonResponse(data)


@csrf_exempt
def cos_post(request, project_id):
    """上传文件提交到数据库"""
    form = UploadPostForm(request.POST)
    if form.is_valid():
        data_dict = form.cleaned_data
        print(data_dict)
        data_dict.update({
            "project": request.project,
            "type": 1,
            "update_user": request.tracer,
        })
        instance = models.FileRepository.objects.create(**data_dict)
        current_project = models.Project.objects.filter(id=project_id).first()
        current_project.use_space += instance.file_size
        current_project.save()
        print(current_project.use_space)
        result = {
            "id": instance.id,
            "name": instance.name,
            "file_size": instance.file_size,
            "update_user": instance.update_user.username,
            "update_time": instance.update_time.strftime("%Y年%m月%d日 %H:%M:%S")
        }
        return JsonResponse({"status": 1, "data": result})
    else:
        print(form.errors)
        return JsonResponse({"status": 0, "data": "文件上传错误"})


def download(request, project_id, file_id):
    """下载文件"""
    file_obj = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    import requests
    data = requests.get(file_obj.file_path).content
    response = HttpResponse(data)
    response['Content-Disposition'] = "attachment; filename={}".format(file_obj.name)
    return response