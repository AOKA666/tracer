from django import forms
from .bootstrap import BootstrapForm
from app01 import models


class FileRepositoryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ["name"]
