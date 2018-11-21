# -*- coding:utf-8 -*-
# course/models.py
from datetime import datetime
from django.db import models

from DjangoUeditor.models import UEditorField
from organization.models import CourseOrg, Teacher


class Course(models.Model):
    DEGREE_CHOICES = (
        ("cj", "初级"),
        ("zj", "中级"),
        ("gj", "高级")
    )
    name = models.CharField("课程名", max_length=50)
    desc = models.CharField("课程描述", max_length=300)
    # detail = models.TextField("课程详情")
    detail = UEditorField(verbose_name=u'课程详情', width=600, height=300, imagePath="courses/ueditor/",
                          filePath="courses/ueditor/", default='')
    degree = models.CharField('难度', choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField("学习时长(分钟数)", default=0)
    students = models.IntegerField("学习人数", default=0)
    fav_nums = models.IntegerField("收藏人数", default=0)
    image = models.ImageField("封面图", upload_to="courses/%Y/%m", max_length=100)
    click_nums = models.IntegerField("点击数", default=0)
    add_time = models.DateTimeField("添加时间", default=datetime.now, )
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构", null=True, blank=True)
    category = models.CharField("课程类别", max_length=20, default="")
    tag = models.CharField('课程标签', default='', max_length=10)
    teacher = models.ForeignKey(Teacher, verbose_name='讲师', null=True, blank=True, on_delete=models.CASCADE)
    youneed_know = models.CharField('课程须知', max_length=300, default='')
    teacher_tell = models.CharField('老师告诉你', max_length=300, default='')
    is_banner = models.BooleanField('是否轮播', default=False)

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    # 获取课程的章节数
    def get_lesson_nums(self):
        return self.lesson_set.all().count()

    # 获取这门课程的学习用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    # 获取这门课程的章节
    def get_course_lesson(self):
        return self.lesson_set.all()

    # 获取课程的章节数
    def get_zj_nums(self):
        return self.lesson_set.all().count()

    get_zj_nums.short_description = '章节数'  # 在后台显示的名称

    # 显示自定义的html代码
    def go_to(self):
        from django.utils.safestring import mark_safe
        # mark_safe后就不会转义
        return mark_safe("<a href='https://home.cnblogs.com/u/derek1184405959/'>跳转</a>")

    go_to.short_description = "跳转"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField("章节名", max_length=100)
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    # 获取章节的video
    def get_lesson_vedio(self):
        return self.video_set.all()

    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course, self.name)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="章节", on_delete=models.CASCADE)
    name = models.CharField("视频名", max_length=100)
    url = models.CharField('访问地址', default='', max_length=200)
    learn_times = models.IntegerField("学习时长(分钟数)", default=0)
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.CASCADE)
    name = models.CharField("名称", max_length=100)
    download = models.FileField("资源文件", upload_to="course/resource/%Y/%m", max_length=100)
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name


class BannerCourse(Course):
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        # 这里必须设置proxy=True，这样就不会再生成一张表，同时还具有Model的功能
        proxy = True
