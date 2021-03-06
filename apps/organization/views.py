# -*- coding:utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse
from pure_pagination import PageNotAnInteger, Paginator
from django.shortcuts import render
from django.views import View

from course.models import Course
from operation.form import UserAskForm
from operation.models import UserFavorite
from utils.mixin_utils import LoginRequiredMixin
from .models import CityDict, CourseOrg, Teacher


class OrgView(View):
    """课程机构"""

    def get(self, request):
        # 默认取出所有课程机构
        all_orgs = CourseOrg.objects.all()
        # 机构搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))
        # 所有授课机构排名，按点击量排名，只取前三个（也可是做成某种类型的或某个城市的机构的排名）
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        # 机构类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)
        org_onums = all_orgs.count()
        # 如果传递过来某个城市的id，那么就显示某个城市的课程机构
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        # 学习人数和课程数筛选
        sort_flag = request.GET.get('sort', '')
        if sort_flag:
            if sort_flag == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort_flag == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')
        # 取出所有城市
        all_citys = CityDict.objects.all()

        # 显示某个机构类别所在的城市，其他城市不显示；弃用不符合逻辑
        # all_citys = list()
        # if all_orgs:
        #     for one_orgs in all_orgs:
        #         print(one_orgs.city)
        #         all_citys.append(one_orgs.city)

        # 对课程机构进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从allorg中取五个出来，每页显示5个
        p = Paginator(all_orgs, 5, request=request)
        all_orgs = p.page(page)
        return render(request, 'org-list.html', locals())


class AddUserAskView(View):
    """用户添加咨询"""

    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """机构首页"""

    def get(self, request, org_id):
        current_page = 'home'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        # 反向查询到课程机构的所有课程和老师
        all_courses = course_org.course_set.all()[:4]
        all_teacher = course_org.teacher_set.all()[:2]
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-homepage.html', {
            'course_org': course_org,
            'all_courses': all_courses,
            'all_teacher': all_teacher,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    """机构课程列表页"""

    def get(self, request, org_id):
        current_page = 'course'
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外键引用
        all_courses = course_org.course_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """机构介绍页"""

    def get(self, request, org_id):
        current_page = 'desc'
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    """机构教师页"""

    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teacher = course_org.teacher_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            'all_teacher': all_teacher,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """用户收藏和取消收藏"""

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)  # 防止后边int(fav_id)时出错
        fav_type = request.POST.get('fav_type', 0)  # 防止int(fav_type)出错

        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                org = CourseOrg.objects.get(id=int(fav_id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"fail", "msg":"已取消收藏"}', content_fav_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    org = CourseOrg.objects.get(id=int(fav_id))
                    org.fav_nums += 1
                    org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


class TeacherListView(View):
    """讲师列表"""

    def get(self, request):
        all_teachers = Teacher.objects.all()
        teachers_num = all_teachers.count()
        # 讲师排行榜
        teachers_ranking_list = all_teachers.order_by('-click_nums')[:3]
        # 老师搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords))
        # 人气排序
        sort_flag = request.GET.get('sort', '')
        if sort_flag:
            if sort_flag == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从all_teachers中取五个出来，每页显示5个
        p = Paginator(all_teachers, 3, request=request)
        teachers = p.page(page)
        return render(request, 'teachers-list.html',
                      {
                          'all_teachers': teachers,
                          'teachers_num': teachers_num,
                          'sorted_teacher': teachers_ranking_list,
                          'sort': sort_flag,

                      })


class TeacherDetailView(LoginRequiredMixin, View):
    """讲师详情"""

    def get(self, request, teacher_id):
        teacher = None
        all_courses = None
        # 教师收藏和机构收藏
        has_teacher_faved = False
        has_org_faved = False
        teacher_list = Teacher.objects.filter(id=int(teacher_id))
        if teacher_list:
            teacher = teacher_list[0]
            teacher.click_nums += 1
            teacher.save()
            # 该教师的全部课程
            all_courses = Course.objects.filter(teacher=teacher)
            # 教师收藏和机构收藏
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher_id):
                has_teacher_faved = True
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True
        # 讲师排行榜，根据点击率排序
        sorted_teachers = Teacher.objects.order_by('-click_nums')[:3]
        return render(request, 'teacher-detail.html',
                      {
                          'teacher': teacher,
                          'all_courses': all_courses,
                          'sorted_teachers': sorted_teachers,
                          'has_teacher_faved': has_teacher_faved,
                          'has_org_faved': has_org_faved,
                      })


