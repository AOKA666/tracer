from django import forms
from app01 import models
from .bootstrap import BootstrapForm


class IssueForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Issue
        exclude = ['project', 'creator', 'create_time', 'last_update_time']
        widgets ={
            "module": forms.Select(attrs={"class": "selectpicker"}),
            "status": forms.Select(attrs={"class": "selectpicker"}),
            "issue_type": forms.Select(attrs={"class": "selectpicker"}),
            "parent": forms.Select(attrs={"class": "selectpicker"}),
            "mode": forms.Select(attrs={"class": "selectpicker"}),
            "priority": forms.Select(attrs={"class": "selectpicker"}),
            "assign": forms.Select(attrs={"class": "selectpicker"}),
            "attention": forms.SelectMultiple(attrs={"class": "selectpicker", "data-live-search":"true"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 父问题列表只能来自当前项目下的问题
        parent_choice = [("", "没有选中任何项")]
        data_list = models.Issue.objects.filter(project=request.project).values_list("id", "subject")
        parent_choice.extend(data_list)
        self.fields['parent'].choices = parent_choice


class IssueRecordForm(forms.ModelForm):
    class Meta:
        model = models.IssueReply
        fields = ['content', 'type', 'parent']