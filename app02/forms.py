import random
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from tracer import local_settings
from app02 import models
from django_redis import get_redis_connection
from app02.utils.sms import send_sms_single
from app02.utils.common import encoder


class BootstrapForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control field"
            field.widget.attrs["placeholder"] = '请输入'+field.label
            field.error_messages['required'] = '此字段必须填写'


class RegisterForm(BootstrapForm, forms.ModelForm):
    username = forms.CharField(label='用户名', min_length=3, max_length=6, error_messages={
        'min_length': '此字段最少3位字符', 'max_length': '此字段最多6位字符'}
    )
    email = forms.EmailField(label='邮箱', error_messages={"invalid": '请输入正确的邮箱格式'})
    phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8}$', '手机号格式错误'),])
    password = forms.CharField(label='密码', min_length=3, widget=forms.PasswordInput(), error_messages={
        'min_length': '密码至少3位'
    })
    confirm_pwd = forms.CharField(label='确认密码', min_length=3, widget=forms.PasswordInput(),error_messages={
        'min_length': '密码至少3位'
    })
    code = forms.CharField(label='验证码')

    def clean_code(self):
        """验证码是否匹配"""
        code = self.cleaned_data.get("code")
        phone = self.cleaned_data.get("phone")
        conn = get_redis_connection()
        redis_code_byte = conn.get(phone)
        if redis_code_byte:
            redis_code = redis_code_byte.decode("utf-8")
            if code != redis_code:
                self.add_error("code", "验证码错误")
        else:
            self.add_error("code", "验证码错误或已过期，请重新获取")
        return code

    def clean_password(self):
        """加密处理"""
        password = self.cleaned_data.get("password")
        return encoder(password)

    def clean_phone(self):
        """验证手机号是否存在"""
        phone = self.cleaned_data.get("phone")
        # 判断手机号是否存在
        exist = models.UserInfo.objects.filter(phone=phone).exists()
        if exist:
            self.add_error("phone", "手机号已存在")
        return phone

    def clean(self):
        """两次密码是否相同"""
        password = self.cleaned_data.get('password')
        confirm_pwd = encoder(self.cleaned_data.get('confirm_pwd'))
        if password != confirm_pwd:
            self.add_error("confirm_pwd", "两次密码不一致")
            return self.cleaned_data

    class Meta:
        model = models.UserInfo
        """前端会按照fields中的顺序来展示"""
        fields = ['username', 'email', 'password', 'confirm_pwd', 'phone', 'code']


class SendSmsForm(forms.Form):
    """发送验证码时验证手机"""
    phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8}$', '手机号格式错误'),])

    def __init__(self, request, *args, **kwargs):
        """为验证tpl传入request"""
        super(SendSmsForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_phone(self):        
        # 验证短信模板是否有问题
        tpl = self.request.GET.get("tpl")
        tpl_id = local_settings.SMS_TEMPLATE.get(tpl)
        if not tpl_id:
            raise ValidationError("短信模板错误")
        phone = self.cleaned_data["phone"]
        # 判断手机号是否存在
        exist = models.UserInfo.objects.filter(phone=phone).exists()
        if tpl == 'register':
            if exist:
                raise ValidationError('手机号已存在')
        elif tpl == 'login':
            if not exist:
                raise ValidationError('手机号不存在，请先注册')
        # 生成验证码
        code = random.randint(1000, 9999)
        print(code)
        sms = send_sms_single(phone, tpl_id, [code,])
        # 发送成功result是0，只要不是0就是发送失败了
        if sms["result"] != 0:
            raise ValidationError("短信发送失败,{}".format(sms['errmsg']))
        # 发送成功，将验证码写入redis
        conn = get_redis_connection()
        conn.set(phone, code, 600)
        return phone


class LoginSmsForm(BootstrapForm, forms.Form):
    phone = forms.CharField(label='手机号', validators=[
        RegexValidator(r'^1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8}$', '手机号格式错误'),])
    code = forms.CharField(label='验证码')

    def clean_phone(self):
        """验证手机号是否存在"""
        phone = self.cleaned_data.get("phone")
        # 判断手机号是否存在,存在的话直接查询出这条数据
        user = models.UserInfo.objects.filter(phone=phone).first()
        print(user)
        if not user:
            self.add_error("phone", "手机号不存在，请先注册")
        return user

    def clean_code(self):
        """验证码是否匹配"""
        code = self.cleaned_data.get("code")
        phone = self.cleaned_data.get("phone").phone
        conn = get_redis_connection()
        redis_code_byte = conn.get(phone)
        if redis_code_byte:
            redis_code = redis_code_byte.decode("utf-8")
            if code != redis_code:
                self.add_error("code", "验证码错误")
        else:
            self.add_error("code", "验证码错误或已过期，请重新获取")
        return code


class LoginForm(BootstrapForm, forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_code(self):
        """验证码是否匹配"""
        code = self.cleaned_data.get("code")
        session_code = self.request.session.get("code")
        if session_code:
            if session_code != code.strip().upper():
                self.add_error("code", "验证码错误")
        else:
            self.add_error("code", "验证码已过期")
        return code

    def clean_password(self):
        # 返回加密的密码
        password = self.cleaned_data.get("password")
        return encoder(password)
