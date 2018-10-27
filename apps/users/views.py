# -*- coding:utf-8 -*-
# users/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from users.models import UserProfile, EmailVerifyRecord
from users.form import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_eamil


class CustomBackend(ModelBackend):
    """
    # 邮箱和用户名都可以登录
    # 基础ModelBackend类，因为它有authenticate方法
    """

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


# def user_login(request):
#     if request.method == 'POST':
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
                return render(request, 'index.html')
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:  # 表单校验没有通过
            return render(request, 'login.html', locals())


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
