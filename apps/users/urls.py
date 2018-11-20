#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time    : 18-11-13 上午11:22
@Author  : TX
@File    : urls.py
@Software: PyCharm
"""
from django.urls import path, re_path

from users.views import UserinfoView, UploadImageView, UpdatePwdView, SendEmailCodeView, UpdateEmailView, \
    MyCourseView, MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessageView

app_name = 'users'

urlpatterns = [
    path('info/', UserinfoView.as_view(), name='user_info'),  # 用户信息
    path("image/upload/", UploadImageView.as_view(), name='image_upload'),  # 用户更改图像
    path("update/pwd/", UpdatePwdView.as_view(), name='update_pwd'),  # 用户个人中心修改密码
    path("sendemail_code/", SendEmailCodeView.as_view(), name='sendemail_code'),  # 发送邮箱修改的验证码
    path("update_email/", UpdateEmailView.as_view(), name='update_email'),  # 修改邮箱
    path("mycourse/", MyCourseView.as_view(), name='mycourse'),  # 我的课程
    path('myfav/org/', MyFavOrgView.as_view(), name="myfav_org"),  # 我的收藏--课程机构
    path('myfav/teacher/', MyFavTeacherView.as_view(), name="myfav_teacher"),  # 我的收藏--授课讲师
    path('myfav/course/', MyFavCourseView.as_view(), name="myfav_course"),  # 我的收藏--课程
    path('my_message/', MyMessageView.as_view(), name="my_message"),  # 我的消息
]



