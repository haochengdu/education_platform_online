#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time    : 18-11-10 下午8:49
@Author  : TX
@File    : mixin_utils.py
@Software: PyCharm
"""
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
