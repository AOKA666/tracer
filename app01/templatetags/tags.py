from django import template
from django.urls import reverse
from app01 import models
register = template.Library()


@register.simple_tag
def render_error(form, field_name):
    return '' if not form.errors.get(field_name) else form.errors.get(field_name)


@register.inclusion_tag("app01/inclusion/all_projects.html")
def fetch_project(request):
    create_project = models.Project.objects.filter(creator=request.tracer)
    join_project = models.ProjectUser.objects.filter(user=request.tracer)
    return {"my": create_project, "join": join_project}


@register.inclusion_tag("app01/inclusion/menu_list.html")
def menu_list(request):
    data_list = [
        {"title": "主页", "url": reverse("app01:dashboard", kwargs={"project_id": request.project.id})},
        {"title": "问题", "url": reverse("app01:issues", kwargs={"project_id": request.project.id})},
        {"title": "数据", "url": reverse("app01:statistics", kwargs={"project_id": request.project.id})},
        {"title": "文件", "url": reverse("app01:file", kwargs={"project_id": request.project.id})},
        {"title": "wiki", "url": reverse("app01:wiki", kwargs={"project_id": request.project.id})},
        {"title": "设置", "url": reverse("app01:settings", kwargs={"project_id": request.project.id})},
    ]
    for item in data_list:
        if request.path_info.startswith(item["url"]):
            item["class"] = "active"
    return {"data_list": data_list}


@register.simple_tag
def render_issue_id(issue_id):
    return str(issue_id).zfill(3)


@register.simple_tag
def render_prefix_dot(issue):
    return 'dot-'+issue.priority