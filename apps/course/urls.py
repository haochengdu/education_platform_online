#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time    : 18-11-6 下午2:03
@Author  : TX
@File    : urls.py
@Software: PyCharm
"""
from django.urls import path, re_path

from course.views import CourseListView, CourseDetailView, CourseInfoView, CommentsView, AddCommentsView, VideoPlayView

# 要写上app的名字
app_name = 'course'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),  # 课程列表
    re_path('course/(?P<course_id>\d+)/', CourseDetailView.as_view(), name='course_detail'),  # 课程详情
    re_path('info/(?P<course_id>\d+)/', CourseInfoView.as_view(), name="course_info"),  # 课程信息，视频及下载
    re_path('comment/(?P<course_id>\d+)/', CommentsView.as_view(), name="course_comments"),  # 课程评论
    path('add_comment/', AddCommentsView.as_view(), name="add_comment"),  # 添加课程评论
    path('video/(?P<video_id>\d+)/', VideoPlayView.as_view(), name="video_play"),  # 课程视频播放页
]
