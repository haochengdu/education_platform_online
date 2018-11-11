import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from pure_pagination import Paginator, PageNotAnInteger

from course.models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


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
        print(course.get_learn_users())
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


class CourseInfoView(LoginRequiredMixin, View):
    """课程章节详情"""

    def get(self, request, course_id):
        course = None
        all_resources = None
        relate_courses = None  # 相关课程，推荐本机构的其他课程
        courses_list = Course.objects.filter(id=int(course_id))
        if courses_list:
            course = courses_list[0]
            # 学习人数加1
            course.students += + 1
            course.save()
            # 查询用户是否已经学习了该课程,如果没有学习该门课程就关联起来
            user_courses = UserCourse.objects.filter(course=course, user=request.user)
            if not user_courses:
                user_course = UserCourse()
                user_course.course = course
                user_course.user = request.user
                user_course.save()
            all_resources = CourseResource.objects.filter(course=course)  # 课程资源
            # 相关课程，推荐本机构的其他课程
            org = course.course_org
            relate_courses = org.course_set.all().order_by('-click_nums')[:3]  # 通过点击数排序
        return render(request, 'course-video.html',
                      {
                          'course': course,
                          'all_resources': all_resources,
                          'relate_courses': relate_courses,
                      })


class CommentsView(LoginRequiredMixin, View):
    """课程评论"""

    def get(self, request, course_id):
        course = None
        all_resources = None
        all_comments = None
        relate_courses = None  # 该课的同学还学过
        courses_list = Course.objects.filter(id=int(course_id))
        if courses_list:
            course = courses_list[0]
            all_resources = CourseResource.objects.filter(course=course)  # 课程资源
            all_comments = CourseComments.objects.all()  # 课程评论
            # 该课的同学还学过
            user_courses = course.usercourse_set.all()  # 学习该课程的用户课程
            user_id_list = [user_course.user.id for user_course in user_courses]  # 学习该课程的所以用户id
            # 通过所有用户的id,找到所有用户学习过的所有课程
            all_user_courses = UserCourse.objects.filter(user_id__in=user_id_list)
            # 取出所有课程id
            course_ids = [user_course.course.id for user_course in all_user_courses]
            # 通过所有课程的id,找到所有的课程，按点击量去五个
            relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        return render(request, 'course-comment.html',
                      {
                          'course': course,
                          'all_resources': all_resources,
                          'all_comments': all_comments,
                          'relate_courses': relate_courses,
                      })


class AddCommentsView(View):
    """添加课程评论"""

    def post(self, request):
        return_msg_dict = dict(status='fail', msg='用户未登陆')
        # 先判断是否登陆，登陆了才可以评论
        if request.user.is_authenticated():
            course_id = request.POST.get('course_id', 0)
            comments = request.POST.get('comments', '')
            if int(course_id) > 0 and comments:
                courses_list = Course.objects.filter(id=int(course_id))
                if courses_list:
                    course = courses_list[0]
                    course_comments = CourseComments()
                    course_comments.course = course
                    course_comments.comments = comments
                    course_comments.user = request.user
                    course_comments.save()
                    return_msg_dict['status'] = 'success'
                    return_msg_dict['msg'] = '评论成功'
                else:
                    return_msg_dict['msg'] = '参数错误'
            else:
                return_msg_dict['msg'] = '参数错误'
        return HttpResponse(json.dumps(return_msg_dict), content_type='application/json')


class VideoPlayView(LoginRequiredMixin, View):
    """课程章节视频播放页面"""

    def get(self, request, video_id):
        video = None
        course = None
        all_resources = None
        relate_courses = None
        video_list = Video.objects.filter(id=video_id)
        if video_list:
            video = video_list[0]
            # 根据video取出本课程
            course = video.lesson.course
            # 查询用户是否已经学习了该课程,如果没有学习该门课程就关联起来
            user_courses = UserCourse.objects.filter(course=course, user=request.user)
            if not user_courses:
                user_course = UserCourse()
                user_course.course = course
                user_course.user = request.user
                user_course.save()
            # 该课的同学还学过
            user_courses = course.usercourse_set.all()  # 学习该课程的用户课程
            user_id_list = [user_course.user.id for user_course in user_courses]  # 学习该课程的所以用户id
            # 通过所有用户的id,找到所有用户学习过的所有课程
            all_user_courses = UserCourse.objects.filter(user_id__in=user_id_list)
            # 取出所有课程id
            course_ids = [user_course.course.id for user_course in all_user_courses]
            # 通过所有课程的id,找到所有的课程，按点击量去五个
            relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
            # 课程资源下载
            all_resources = course.courseresource_set.filter(course=course)
        return render(request, 'course-play.html',
                      {
                          "video": video,
                          "course": course,
                          "all_resources": all_resources,
                          "relate_courses": relate_courses,
                      })








