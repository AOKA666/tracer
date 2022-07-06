from app01 import models
from .bootstrap import BootstrapForm
from django import forms


class ProjectForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea
        }