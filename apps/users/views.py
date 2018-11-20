# -*- coding:utf-8 -*-
# users/views.py
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from pure_pagination import Paginator, PageNotAnInteger

from course.models import Course
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from users.models import UserProfile, EmailVerifyRecord, Banner
from users.form import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_eamil
from utils.mixin_utils import LoginRequiredMixin


class CustomBackend(ModelBackend):
    """
    # 邮箱和用户名都可以登录
    # 基础ModelBackend类，因为它有authenticate方法
    """

    # 凡是调用authenticate都会调用这个函数来进行验证
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            print(e)
            return None


class IndexView(View):
    """首页"""

    def get(self, request):
        # 轮播图
        all_banners = Banner.objects.all().order_by('index')
        # 不轮播的课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })

        # def user_login(request):


# if request.method == 'POST':
#         # 获取用户提交的用户名和密码
#         user_name = request.POST.get('username', None)
#         pass_word = request.POST.get('password', None)
#         # 成功返回user对象,失败None
#         user = authenticate(username=user_name, password=pass_word)
#         # 如果不是null说明验证成功
#         if user is not None:
#             # 登录
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg': '用户名或密码错误'})
#     elif request.method == 'GET':
#         return render(request, 'login.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象,失败None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是null说明验证成功
            if user is not None:
                # 登录
                login(request, user)
                # return render(request, 'index.html')
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:  # 表单校验没有通过
            return render(request, 'login.html', locals())


class LogoutView(View):
    """用户登出"""

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', locals())

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', None)
            # 如果用户已存在，则提示错误信息
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已存在'})

            pass_word = request.POST.get('password', None)
            # 实例化一个user_profile对象
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            # 对保存到数据库的密码加密
            user_profile.password = make_password(pass_word)
            user_profile.save()
            send_register_eamil(user_name, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    """激活用户的view"""

    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                # 这里可以做一个多久激活有效
                user.is_active = True
                user.save()
                # 激活成功跳转到登录页面
                return render(request, "login.html", )
        # 自己瞎输的验证码
        else:
            return render(request, "register.html", {"msg": "您的激活链接无效"})


class ForgetPwdView(View):
    """找回密码"""

    def get(self, request):
        return render(request, 'forgetpwd.html')

    def post(self, request):
        forget_pwd = ForgetPwdForm(request.POST)
        if forget_pwd.is_valid():
            email_num = request.POST.get('email', None)
            # 这里需要判断该email是否存在，存在才发邮件，不存在弹出提示信息
            send_register_eamil(email_num, 'forget')
            render(request, 'send_success.html')
        else:
            print('忘记密码表单校验失败')
            return render(request, 'forgetpwd.html', {'forget_pwd': forget_pwd})


class ResetView(View):
    """重置密码"""

    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                email_num = record.email
                return render(request, "password_reset.html", {"email": email_num})
        else:
            return render(request, "active_fail.html")


class ModifyPwdView(View):
    """修改密码"""

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致！"})
            user_list = UserProfile.objects.filter(email=email)
            if user_list:
                user = user_list[0]
                user.password = make_password(pwd2)
                user.save()
                return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


class UserinfoView(LoginRequiredMixin, View):
    """用户个人信息"""

    def get(self, request):
        return render(request, 'usercenter-info.html')

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            print(user_info_form.errors)
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """用户更改图像"""

    def post(self, request):
        # 上传的文件都在request.FILES里面获取，所以这里要多传一个这个参数
        image_form = UploadImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """用户个人中心修改密码"""

    def post(self, request):
        modify_pwd_form = ModifyPwdForm(request.POST)
        if modify_pwd_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')
            request.user.password = make_password(pwd1)
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_pwd_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """发送邮箱修改的验证码"""

    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')
        send_register_eamil(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """修改邮箱"""

    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """我的课程"""

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html',
                      {
                          'user_courses': user_courses,
                      })


class MyFavOrgView(LoginRequiredMixin, View):
    """我收藏的课程机构"""

    def get(self, request):
        org_list = []
        user_fav_org_list = UserFavorite.objects.filter(user=request.user, fav_type=2)
        if user_fav_org_list:
            for user_fav_org in user_fav_org_list:
                fav_org = CourseOrg.objects.get(id=user_fav_org.fav_id)  # 根据机构id查询出机构对象，存入列表
                org_list.append(fav_org)
        return render(request, 'usercenter-fav-org.html',
                      {
                          'org_list': org_list,
                      })


class MyFavTeacherView(LoginRequiredMixin, View):
    """我的收藏--授课讲师"""

    def get(self, request):
        teacher_list = []
        user_fav_teacher_list = UserFavorite.objects.filter(user=request.user, fav_type=3)
        if user_fav_teacher_list:
            for user_fav_teacher in user_fav_teacher_list:
                fav_teacher = Teacher.objects.get(id=user_fav_teacher.fav_id)  # 根据机构id查询出机构对象，存入列表
                teacher_list.append(fav_teacher)
        return render(request, 'usercenter-fav-teacher.html',
                      {
                          'teacher_list': teacher_list,
                      })


class MyFavCourseView(LoginRequiredMixin, View):
    """我的收藏--课程"""

    def get(self, request):
        course_list = []
        user_fav_course_list = UserFavorite.objects.filter(user=request.user, fav_type=1)
        if user_fav_course_list:
            for user_fav_course in user_fav_course_list:
                fav_course = Course.objects.get(id=user_fav_course.fav_id)  # 根据机构id查询出机构对象，存入列表
                course_list.append(fav_course)
        return render(request, 'usercenter-fav-course.html',
                      {
                          'course_list': course_list,
                      })


class MyMessageView(LoginRequiredMixin, View):
    """我的消息"""

    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 6, request=request)
        messages = p.page(page)
        return render(request, 'usercenter-message.html',
                      {
                          'messages': messages,
                      })


def pag_not_found(request):
    """全局404处理函数"""

    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    """全局500处理函数"""

    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response



