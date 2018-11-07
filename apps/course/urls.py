#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time    : 18-11-6 下午2:03
@Author  : TX
@File    : urls.py
@Software: PyCharm
"""
from django.urls import path, re_path

from course.views import CourseListView, CourseDetailView

# 要写上app的名字
app_name = 'course'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
    re_path('course/(?P<course_id>\d+)/', CourseDetailView.as_view(), name='course_detail'),
]
