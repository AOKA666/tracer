import json
import datetime
from django .shortcuts import render
from app01.forms.issues import IssueForm, IssueRecordForm, InviteForm
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from django.conf import settings
from app01 import models
from app01.utils.func.issue_record import reply_record
from app01.utils.common import encoder, uid


class GenerateFilter:
    """封装过滤器"""
    def __init__(self, name, choice_list, request, select_name):
        """

        :param name: 筛选参数的名字，例如 status, issue_type
        :param choice_list: 筛选内容集，例如[('danger',’高'),('warning','中'),('success','低')]
        :param request:
        :param select_name: 标签被选中时的属性名，例如 selected, checked
        """
        self.choice_list = choice_list
        self.request = request
        self.name = name
        self.select_name = select_name

    def __iter__(self):
        for item in self.choice_list:
            param_list = self.request.GET.getlist(self.name)
            key = item[0]
            text = item[1]
            ck = ""
            if str(key) in param_list: # 当前是选中的，则下一次点击应该剔除
                ck = self.select_name
                if str(key) in param_list:
                    param_list.remove(str(key))
            else:
                param_list.append(str(key))

            href = self.get_new_url(param_list)
            html = self.get_html(href, text, ck)
            yield mark_safe(html)

    def get_new_url(self, param_list):
        path = self.request.GET.copy()
        path._mutable = True
        path.setlist(self.name, param_list)

        href = "{}?{}".format(self.request.path_info, path.urlencode())
        if not path.urlencode():
            href = self.request.path_info
        return href

    def get_html(self, href, text, ck, *args, **kwargs):
        pass


class CheckFilter(GenerateFilter):
    def get_html(self, href, text, ck, *args, **kwargs):
        return f'<a href="{href}"><input type="checkbox" {ck} />{text}</a>'
            

class SelectFilter(GenerateFilter):
    def get_html(self, href, text, ck, *args, **kwargs):
        return f'<option value="{href}" {ck} class="filter-user">{text}<option/>'


def issues(request, project_id):
    if request.method == 'GET':
        allow_filter_name = ["status", "issue_type", "priority", "assign", "attention"]
        conditions = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue           
            conditions["{}__in".format(name)] = value_list
        print(conditions)
        # 左侧筛选栏
        # 状态
        filter_status = CheckFilter('status', models.Issue.status_choices, request, "checked")
        # 优先级
        filter_priority = CheckFilter('priority', models.Issue.priority_choices, request, "checked")
        # 问题类型
        issue_type_list = models.IssueType.objects.filter(project_id=project_id).values_list("id", "title")
        filter_issue_type = CheckFilter('issue_type', issue_type_list, request, "checked")
        # 指派和关注，需要列举出项目的创建者和参与者
        user_list = [(request.project.creator.id, request.project.creator.username)]
        project_user_list = models.ProjectUser.objects.filter(project_id=project_id).values_list("user_id", "user__username")
        user_list.extend(list(project_user_list))
        filter_assign = SelectFilter('assign', user_list, request, "selected")
        filter_attention =  SelectFilter('attention', user_list, request, "selected")

        issue_list = models.Issue.objects.filter(project_id=project_id).filter(**conditions).order_by("-id")
        # 分页
        paginator = Paginator(issue_list, per_page=settings.ISSUE_PER_PAGE)
        current_page = request.GET.get("page", "1")
        if not current_page.isdecimal():
            current_page = 1
        if int(current_page) > paginator.num_pages or int(current_page) < 0:
            current_page = int(paginator.num_pages)
        else:
            current_page = int(current_page)
        query_set = paginator.page(current_page)
        form = IssueForm(request)
        invite_form = InviteForm()
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


@csrf_exempt
def generate_code(request, project_id):
    form = InviteForm(request.POST)
    if form.is_valid():
        # 1.邀请人是不是项目创建者
        if request.project.creator != request.tracer:
            return JsonResponse({"status": False, "msg": "只有项目创建者可以邀请"})
        # 2.数量是否超限
        input_count = request.POST.get("count", None)
        if input_count:
            # 套餐允许的最大数量
            max_count = request.price_policy.price_policy.project_member
            if int(input_count)+1 > max_count:
                return JsonResponse({"status": False, "msg": "超过最大邀请数量 {}".format(max_count-1)})

        # 可以生成随机邀请码
        random_code = encoder(uid(request.project.name))
        scheme = request.scheme
        host = request.get_host()
        path = reverse("app01:invite_join", kwargs={"code": random_code})
        invite_code = "{}://{}{}".format(scheme, host, path)
        print(invite_code)
        instance = models.ProjectInvite.objects.create(
            project_id=project_id,
            code=random_code,
            period=request.POST.get("period"),
            inviter=request.tracer
        )
        if input_count:
            instance.count = input_count
        else:
            instance.count = request.price_policy.price_policy.project_member-1
        instance.save()
        return JsonResponse({"status": True, "msg": invite_code})
    return JsonResponse({"status": False, "msg": form.errors})


def invite_join(request, code):
    invite_obj = models.ProjectInvite.objects.filter(code=code).first()
    # 1.邀请码是否正确
    if not invite_obj:
        error_msg = "邀请码错误"
        return render(request, "app01/project_invite.html", {"status":False,"error_msg": error_msg})
    # 2.项目创建者无法再加入
    if request.tracer == invite_obj.project.creator:
        error_msg = "项目创建者无需加入项目"
        return render(request, "app01/project_invite.html", {"status":False,"error_msg": error_msg})
    # 3.是否已经加入项目
    user_join = models.ProjectUser.objects.filter(project=invite_obj.project, user=request.tracer).first()
    if user_join:
        error_msg = "已加入项目，无法重复加入"
        return render(request, "app01/project_invite.html", {"status":False,"error_msg": error_msg})
    # 4.邀请码是否过期
    period = invite_obj.period
    current_time = datetime.datetime.now()
    create_time = invite_obj.create_time
    if create_time + datetime.timedelta(minutes=period) < current_time:
        error_msg = "邀请码已过期"
        return render(request, "app01/project_invite.html", {"status":False,"error_msg": error_msg})
    # 5.是否超过数量限制
    max_count = invite_obj.count
    used_count = invite_obj.use_count
    current_count = models.ProjectUser.objects.filter(project=invite_obj.project).count()
    if current_count+used_count >= max_count:
        error_msg = "超过项目成员数量限制，无法加入"
        return render(request, "app01/project_invite.html", {"status":False,"error_msg": error_msg})
    # 6.可以加入
    print("可以加入")
    models.ProjectUser.objects.create(
        user=request.tracer,
        project=invite_obj.project,
        inviter=invite_obj.inviter
    )
    invite_obj.use_count += 1
    invite_obj.save()
    return render(request, "app01/project_invite.html", {"status": True})