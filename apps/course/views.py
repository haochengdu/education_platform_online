from django.shortcuts import render
from django.views import View
from pure_pagination import Paginator, PageNotAnInteger

from course.models import Course
from operation.models import UserFavorite


class CourseListView(View):
    """课程列表页"""

    def get(self, request):
        # 查询出所有的课程
        all_courses = Course.objects.all()
        # 热门课程推荐
        hot_courses = all_courses.order_by('-click_nums')[:3]
        # 排序
        sort_flag = request.GET.get('sort', '')
        if sort_flag:
            if sort_flag == 'students':
                # 根据学习人数排序
                all_courses = all_courses.order_by('-students')
            elif sort_flag == 'hot':
                # 根据点击数排序
                all_courses = all_courses.order_by('-click_nums')
            else:
                # 默认，根据最新排序
                all_courses = all_courses.order_by('-add_time')
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 6, request=request)
        courses = p.page(page)
        return render(request, 'course-list.html',
                      {
                          'all_courses': courses,
                          'hot_courses': hot_courses,
                      })


class CourseDetailView(View):
    """课程详情"""
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 课程的点击数加1
        course.click_nums += 1
        course.save()
        # 课程标签
        # 通过当前标签，查找数据库中相同标签的课程来推荐
        tag = course.tag
        if tag:
            # 需要从1开始不然会推荐自己
            relate_courses = Course.objects.filter(tag=tag)[:3]
        else:
            relate_courses = []
        # 是否收藏课程或者机构
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.all().filter(user=request.user, fav_type=1, fav_id=course_id):
                has_fav_course = True
            if UserFavorite.objects.all().filter(user=request.user, fav_type=2, fav_id=course.course_org.id):
                has_fav_org = True
        return render(request, 'course-detail.html',
                      {
                          'course': course,
                          'relate_courses': relate_courses,
                          'has_fav_course': has_fav_course,
                          'has_fav_org': has_fav_org,
                      })



