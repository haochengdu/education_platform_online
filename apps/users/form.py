# -*- coding:utf-8 -*-
# users/forms.py
from django import forms
from captcha.fields import CaptchaField

from users.models import UserProfile


class LoginForm(forms.Form):
    """登录表单验证"""
    # 用户名密码不能为空
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    """注册验证表单"""
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    # 验证码，字段里面可以自定义错误提示信息
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ForgetPwdForm(forms.Form):
    """找回密码"""
    email = forms.EmailField(required=True)
    # captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    """修改密码"""
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    """用户更改图像表单"""

    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    """个人中心信息修改"""

    class Meta:
        model = UserProfile
        fields = ['nick_name', 'birthday', 'gender', 'address', 'mobile']
