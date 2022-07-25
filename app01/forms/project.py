from app01 import models
from .bootstrap import BootstrapForm
from django import forms
from django.forms import RadioSelect


class ColorSelect(RadioSelect):
    input_type = 'radio'
    template_name = 'app01/widgets/radio.html'
    option_template_name = 'app01/widgets/color_option.html'


class ProjectForm(BootstrapForm, forms.ModelForm):
    bootstrap_exclude = ['color']

    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorSelect
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')
        exists = models.Project.objects.filter(name=name, creator=self.request.tracer).exists()
        if exists:
            self.add_error('name', '项目名重复！')
        max_num = self.request.price_policy.price_policy.project_num
        current = self.request.tracer.project_set.count()
        if current >= max_num:
            self.add_error('name', '已超过创建项目最大数量，请充值')
        return name