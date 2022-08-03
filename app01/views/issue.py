from django .shortcuts import render
from app01.forms.issues import IssueForm
from django.http import JsonResponse
from app01 import models


def issues(request, project_id):
    if request.method == 'GET':
        issue_list = models.Issue.objects.all()
        form = IssueForm(request)
        return render(request, 'app01/issues.html', {"form":form, "issue_list": issue_list})
    print(request.POST)
    form = IssueForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project_id = project_id
        form.instance.creator = request.tracer
        instance = form.save()
        dataDict = {
            "issue_type": instance.get_issue_type,
            "subject": instance.subject,
            "status": instance.get_status_display,
            "assign": instance.assign__username,
            "attention": instance.attention__username,
            "start_date": instance.start_date.strftime("%Y-%m-%d, %H:%M:%S"),
            "end_date": instance.end_date.strftime("%Y-%m-%d, %H:%M:%S"),
        }
        return JsonResponse({"status": True, "data": dataDict})
    else:
        return JsonResponse({"status": False, "data": form.errors})
