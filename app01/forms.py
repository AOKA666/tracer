from django import forms
from django.core.validators import RegexValidator

from app01 import models
from app01.utils import redis


class RegisterForm(forms.ModelForm):
    phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8}$','手机号格式错误'),])
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_pwd = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = '请输入'+field.label

    def clean_code(self):
        code = self.cleaned_data.get("code")
        conn = redis.connect()
        redis_code_byte = conn.get("code")
        if redis_code_byte:
            redis_code = redis_code_byte.decode("utf-8")
            if code != redis_code:
                self.add_error("code", "验证码错误")
        else:
            self.add_error("code", "验证码已过期，请重新获取")
        return code

    def clean(self):
        password = self.cleaned_data['password']
        confirm_pwd = self.cleaned_data['confirm_pwd']
        if password != confirm_pwd:
            self.add_error("confirm_pwd", "两次密码不一致")
            return self.cleaned_data

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_pwd', 'phone', 'code']