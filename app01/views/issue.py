import json

from django .shortcuts import render
from app01.forms.issues import IssueForm, IssueRecordForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from app01 import models
from app01.utils.func.issue_record import reply_record


class CheckFilter:
    """前端checkbox过滤器"""
    def __init__(self, name, choice_list, request):
        self.choice_list = choice_list
        self.request = request
        self.name = name

    def __iter__(self):
        # 下一次查询的参数列表      
        for item in self.choice_list:
            param_list = self.request.GET.getlist(self.name)
            key = item[0]
            text = item[1]
            ck = ""         
            if str(key) in param_list: # 当前是选中的，则下一次点击应该剔除
                ck = "checked"
                if str(key) in param_list:
                    param_list.remove(str(key))
            else:
                param_list.append(str(key))
            # 构造新的过滤链接
            path = self.request.GET.copy()
            path._mutable = True
            path.setlist(self.name, param_list)

            href = "{}?{}".format(self.request.path_info, path.urlencode())
            html = f'<a href="{href}"><input type="checkbox" {ck} />{text}</a>'
            yield mark_safe(html)
            

class SelectFilter:
    """前端select过滤器"""
    def __init__(self, name, choice_list, request):
        self.choice_list = choice_list
        self.request = request
        self.name = name

    def __iter__(self):    
        for item in self.choice_list:
            param_list = self.request.GET.getlist(self.name)
            key = item[0]
            text = item[1]
            selected = ""         
            if str(key) in param_list: # 当前是选中的，则下一次点击应该剔除
                selected = "selected"
                param_list.remove(str(key))
            else:
                param_list.append(str(key))
            # 构造新的过滤链接
            path = self.request.GET.copy()
            path._mutable = True
            path.setlist(self.name, param_list)

            href = "{}?{}".format(self.request.path_info, path.urlencode())
            html = f'<option value="{href}" {selected} class="filter-user">{text}<option/>'
            yield mark_safe(html)
    

def issues(request, project_id):
    if request.method == 'GET':
        allow_filter_name = ["status", "issue_type", "priority"]
        conditions = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue           
            conditions["{}__in".format(name)] = value_list
        # 左侧筛选栏
        # 状态
        filter_status = CheckFilter('status', models.Issue.status_choices, request)
        # 优先级
        filter_priority = CheckFilter('priority', models.Issue.priority_choices, request)
        # 问题类型
        issue_type_list = models.IssueType.objects.filter(project_id=project_id).values_list("id", "title")
        filter_issue_type = CheckFilter('issue_type', issue_type_list, request)
        # 指派和关注，需要列举出项目的创建者和参与者
        user_list = [(request.project.creator.id, request.project.creator.username)]
        project_user_list = models.ProjectUser.objects.filter(project_id=project_id).values_list("id", "user__username")
        user_list.extend(list(project_user_list))
        filter_assign = SelectFilter('assign', user_list, request)
        filter_attention =  SelectFilter('attention', user_list, request)

        issue_list = models.Issue.objects.filter(project_id=project_id).filter(**conditions).order_by("-id")
        # 分页
        paginator = Paginator(issue_list, per_page=5)
        current_page = request.GET.get("page", "1")
        if not current_page.isdecimal():
            current_page = 1
        if int(current_page) > paginator.num_pages or int(current_page) < 0:
            current_page = int(paginator.num_pages)
        else:
            current_page = int(current_page)
        query_set = paginator.page(current_page)
        form = IssueForm(request)
        return render(request, 'app01/issues.html', locals())
    form = IssueForm(request, data=request.POST)
    if form.is_valid():
        result_dict = form.cleaned_data
        result_dict.update({"project_id": project_id, "creator": request.tracer})
        form.instance.project_id = project_id
        form.instance.creator = request.tracer
        form.save()
        return JsonResponse({"status": True})
    else:
        return JsonResponse({"status": False, "data": form.errors})


def details(request, project_id, issue_id):
    issue_obj = models.Issue.objects.filter(id=issue_id, project_id=project_id).first()
    form = IssueForm(request, instance=issue_obj)
    return render(request, 'app01/issue_details.html', {"form": form, "issue_obj": issue_obj})


@csrf_exempt
def record(request, project_id, issue_id):
    if request.method == 'GET':
        reply_list = models.IssueReply.objects.filter(issue_id=issue_id).order_by("depth").values(
            "id", "content", "parent_id", "creator__username", "time", "type")
        result = list(reply_list)
        # 更改时间格式
        for each in result:
            each['time'] = each['time'].strftime("%Y-%m-%d %H:%M:%S")
        return JsonResponse({"data": result})
    form = IssueRecordForm(request.POST)
    if form.is_valid():
        form.instance.issue_id = issue_id
        form.instance.creator = request.tracer
        parent_id = request.POST.get("parent")
        if parent_id:
            form.instance.depth = models.IssueReply.objects.get(id=parent_id).depth + 1
        else:
            form.instance.depth = 1
        instance = form.save()
        result_dict = [{
            "id": instance.id,
            "content": instance.content,
            "parent_id": instance.parent_id,
            "creator__username": instance.creator.username,
            "time": instance.time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": instance.type,
            "avatar": instance.creator.username[0]
        }]
        return JsonResponse({"status": True, "data": result_dict})
    else:
        return JsonResponse({"status": False, "errors": form.errors})


@csrf_exempt
def data_change(request, project_id, issue_id):
    data_dict = json.loads(request.body.decode("utf-8"))
    print(data_dict)
    issue_obj = models.Issue.objects.filter(id=issue_id, project_id=project_id).first()
    """
    判断数据来源
        1. 输入框：subject, content, start_time, end_time
        2. 下拉框：mode, status, priority
        3. 外键：type, module, parent, assign
        4. 多对多：attention
    """
    name = data_dict.get("name")
    value = data_dict.get("value")
    field = models.Issue._meta.get_field(name)

    # 输入框：subject, content, start_time, end_time
    if name in ["subject", "content", "start_date", "end_date"]:
        if not value:
            # 是否允许为空
            if not field.null:
                return JsonResponse({"status": False, "msg": "该字段不能为空"})
            else:
                setattr(issue_obj, name, value)
                issue_obj.save()
                record = "{}更新为空".format(field.verbose_name)
                return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
        else:
            setattr(issue_obj, name, value)
            issue_obj.save()
            record = "<{}>更新为: {}".format(field.verbose_name, value)
            return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
    # 选择框：type, module, mode, status, priority
    elif name in ["mode", "status", "priority"]:
        for k,v in field.choices:
            print(k,v)
            if k == value:
                # 存在这个选项
                setattr(issue_obj, name, value)
                issue_obj.save()
                record = "<{}>更新为: {}".format(field.verbose_name, v)
                return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
        return JsonResponse({"status": False, "msg": "选项不存在"})
    # 外键：issue_type, module, parent, assign
    elif name in ["issue_type", "module", "parent", "assign"]:
        if not value:
            if not field.null:
                return JsonResponse({"status": False, "msg": "该字段不能为空"})
            else:
                setattr(issue_obj, name, None)
                issue_obj.save()
                record = "<{}>更新为空".format(field.verbose_name)
                return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
        else:
            # 指派，必须是项目创建者或参与者
            if name == 'assign':
                user_id = request.project.creator_id
                # 判断是否是项目创建者
                if str(user_id) == value:
                    instance = request.project.creator
                else:
                    # 判断是否是项目参与者
                    project_user = models.ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user:
                        instance = project_user.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({"status": False, "msg": "非法用户"})
                setattr(issue_obj, name, instance)
                issue_obj.save()
                record = "<{}>更新为: {}".format(field.verbose_name, str(instance))
                return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
            related_model = field.remote_field.model # 获取外键关联的模型
            instance = related_model.objects.filter(id=value, project_id=project_id).first()
            if not instance:
                return JsonResponse({"status": False, "msg": "选项不存在"})
            else:
                setattr(issue_obj, name, instance)
                issue_obj.save()
                record = "<{}>更新为: {}".format(field.verbose_name, str(instance))
                return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
    # m2m：attention
    # {'name': 'attention', 'value': ['2', '3']},判断value是否是当前项目成员
    elif name == 'attention':
        if not value:
            issue_obj.attention.set([])
            issue_obj.save()
            record = "{}更新为空".format(field.verbose_name)
            return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
        else:
            # {'1': 'wcy', '2': 'bby'}
            user_dict = {str(request.project.creator.id): request.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(user_id)
                if not username:
                    return JsonResponse({"status": False, "msg": "非法用户"})
                username_list.append(username)
            # 数据没问题
            issue_obj.attention.set(value)
            issue_obj.save()
            record = "<{}>更新为: {}".format(field.verbose_name, ','.join(username_list))
            return JsonResponse({"status": True, "data": reply_record(request, issue_obj, record)})
    return JsonResponse({"status": False, "data": "想黑我？！"})