"""education_platform_online URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

import xadmin
from education_platform_online.settings import MEDIA_ROOT, STATIC_ROOT
from organization.views import OrgView
from users import views
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, \
    IndexView

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    # path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('', IndexView.as_view(), name='index'),
    # path('login/', views.user_login, name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    # path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('captcha/', include('captcha.urls')),
    re_path('active/(?P<active_code>.*)/', ActiveUserView.as_view(), name='user_active'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    re_path('reset/(?P<active_code>.*)/', ResetView.as_view(), name='reset_pwd'),
    path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),
    # path('org_list/', OrgView.as_view(), name='org_list'),
    path("org/", include('organization.urls', namespace="org")),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path('^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
    path('course/', include('course.urls', namespace='course')),
    path('users/', include('users.urls', namespace='users')),
    # 富文本编辑器url
    path('ueditor/', include('DjangoUeditor.urls')),
    # 404和500,生成环境汇总，必须设置debug = False
    # 一旦debug改为false，django就不会代管你的静态文件，所以这里要设置一个url处理静态文件
    # re_path(r'^static/(?P<path>.*)', serve, {"document_root": STATIC_ROOT}),
]

# 全局404页面配置,当django的settings中DEBUG = False时后会自动调用，需要重新配置静态文件，DEBUG = True时的静态文件会失效
handler404 = 'users.views.pag_not_found'

handler500 = 'users.views.page_error'
