# -*- coding:utf-8 -*-
# course/adminx.py
import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    """课程"""
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'get_zj_nums', 'go_to']  # 显示的内容
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']  # 查询
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']  # 过滤
    model_icon = 'fa fa-book'  # 图标
    ordering = ['-click_nums']  # 排序
    readonly_fields = ['click_nums']  # 只读字段，不能编辑
    exclude = ['fav_nums']  # 不显示的字段
    # 目前在添加课程的时候没法添加章节和课程资源，我们可以用inlines去实现这一功能
    inlines = [LessonInline, CourseResourceInline]
    list_editable = ['desc', 'detail']  # 在列表页可以直接编辑的
    refresh_times = [3, 5, 10]  # 自动刷新（里面是秒数）
    # detail就是要显示为富文本的字段名
    style_fields = {"detail": "ueditor"}
    import_excel = True  # 是否显示导入excel的接口

    def queryset(self):
        # 重载queryset方法，来过滤出我们想要的数据的
        qs = super(CourseAdmin, self).queryset()
        # 只显示is_banner=True的课程
        qs = qs.filter(is_banner=False)
        return qs

    # 应用场景：当添加一门课程的时候，希望课程机构里面的课程数 + 1
    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    def post(self, request, *args, **kwargs):
        """对上传的excel的操作"""
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs)


class BannerCourseAdmin(object):
    """轮播课程"""
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']  # 显示的内容
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']  # 查询
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']  # 过滤
    model_icon = 'fa fa-book'  # 图标
    ordering = ['-click_nums']  # 排序
    readonly_fields = ['click_nums']  # 只读字段，不能编辑
    exclude = ['fav_nums']  # 不显示的字段
    # 目前在添加课程的时候没法添加章节和课程资源，我们可以用inlines去实现这一功能
    inlines = [LessonInline, CourseResourceInline]

    def queryset(self):
        # 重载queryset方法，来过滤出我们想要的数据的
        qs = super(BannerCourseAdmin, self).queryset()
        # 只显示is_banner=True的课程
        qs = qs.filter(is_banner=True)
        return qs

    # 应用场景：当添加一门课程的时候，希望课程机构里面的课程数 + 1
    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


class LessonAdmin(object):
    """章节"""
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 这里course__name是根据课程名称过滤
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    """视频"""
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    """课程资源"""
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']


# 将管理器与model进行注册关联
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
