from django import forms
from .bootstrap import BootstrapForm
from app01 import models


class FileRepositoryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ["name"]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get("name")
        queryset = models.FileRepository.objects.filter(name=name, project=self.request.project, type=2)
        parent_id = self.request.GET.get("folder", "")
        if parent_id.isdecimal():
            exist = queryset.filter(parent_id=parent_id).exists()
        else:
            exist = queryset.filter(parent__isnull=True).exists()
        if exist:
            self.add_error("name", "文件夹已存在")
        return name


class EditFolderForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ["name"]


class UploadPostForm(forms.ModelForm):
    class Meta:
        model = models.FileRepository
        exclude = ["project", "type", "update_user", "update_time"]

    def clean_file_path(self):
        return "https://{}".format(self.cleaned_data.get("file_path"))