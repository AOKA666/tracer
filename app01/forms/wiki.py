from django import forms
from app01 import models
from app01.forms.bootstrap import BootstrapForm


class WikiForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent_choice = [("", "请选择")]
        data_list = models.Wiki.objects.filter(project=request.project).values_list("id", "title")
        parent_choice.extend(data_list)
        self.fields['parent'].choices = parent_choice
