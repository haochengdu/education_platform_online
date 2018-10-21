# -*- coding:utf-8 -*-
# users/forms.py
from django import forms


class LoginForm(forms.Form):
    """登录表单验证"""
    # 用户名密码不能为空
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)
