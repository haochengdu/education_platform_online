# django总结
### setting
#### 1. 扩展包，加入到项目根目录
```
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
```
#### 2. 模板路径及在前端页面使用MEDIA_URL路径
```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 添加图片处理器，为了在课程列表中前面加上MEDIA_URL
                'django.template.context_processors.media',
            ],
        },
    },
]
```
#### 3. 使用django后台时候汉字及时间的显示
```
LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False
```
#### 4. 使用自定义的user替代django系统自带的user
```
AUTH_USER_MODEL = 'users.UserProfile'
```
#### 5. 在debug模式下对静态文件的设置
```
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
```
#### 6. 设置上传文件路径的设置
```
# 设置上传文件的路径
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 指定根目录
```
#### 7. 使用新浪邮箱发送邮件
```
# 使用新浪邮箱发邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sina.cn'
EMAIL_PORT = 25
# EMAIL_HOST_USER = '新浪邮箱账号@sina.cn'
EMAIL_HOST_USER = 'xxxxxxxxxm@sina.cn'
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxx'
# 注册有效期天数
CONFIRM_DAYS = 7
```
#### 8. 设置自定义的authenticate
```
# 设置自定义的验证类
AUTHENTICATION_BACKENDS = (
    'users.views.CustomBackend',
)
```
### url
#### 1. TemplateView 使用，直接返回一个html页面
```
from django.views.generic import TemplateView
path('', TemplateView.as_view(template_name='index.html'), name='index'),
```
#### 2. view 函数 需要先到views里定义该函数
```
from users import views
path('login/', views.user_login, name='login'),
```
#### 3. view类 需要现在views里定义该类并继承view
```
from django.urls import path, include, re_path
from users.views import LoginView, ActiveUserView
path('login/', LoginView.as_view(), name='login'),
re_path('active/(?P<active_code>.*)/', ActiveUserView.as_view(), name='user_active'),
```
#### 4. 二级路由
```
from django.urls import path, include
path('course/', include('course.urls', namespace='course')),
```
#### 5. 前端图片路径
```
from django.views.static import serve
from education_platform_online.settings import MEDIA_ROOT
# 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
re_path('^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
```
#### 6. 富文本路径
```
# 富文本编辑器url，需要在setting里INSTALL_APPS里注册DjangoUeditor
path('ueditor/', include('DjangoUeditor.urls')),
```

### model
#### 1. 对django自带的user的继承覆盖
```
from django.contrib.auth.models import AbstractUser
class UserProfile(AbstractUser):
    gender_choices = (
        ('male', '男'),
        ('female', '女')
    )

    nick_name = models.CharField('昵称', max_length=50, default='')
    birthday = models.DateField('生日', null=True, blank=True)
    gender = models.CharField('性别', max_length=10, choices=gender_choices, default='female')
    address = models.CharField('地址', max_length=100, default='')
    mobile = models.CharField('手机号', max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to='image/%Y%m', default='image/default.png', max_length=100)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
```
#### 2. 普通model只需要继承model.Model
```
from django.db import models
from DjangoUeditor.models import UEditorField

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
                          filePath="courses/ueditor/", default='')  # 对富文本的使用，需首先配置富文本
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
        # ordering = ['id']  # 根据id正序(也是默认的排序)

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
```

### form表单
#### 1. 自定义表单
```
class RegisterForm(forms.Form):
    """注册验证表单"""
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    # 验证码，字段里面可以自定义错误提示信息
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})
```
#### 2. 继承forms.ModelForm的表单
```
import re

from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm):
    """我要咨询"""

    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']  # 表单字段

    def clean_mobile(self):
        """
        验证手机号码是否合法
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")
```
### xadmin
#### 1. 普通注册
```
class UserCourseAdmin(object):
    """户课程学习"""
    list_display = ['user', 'course', 'add_time']  # 后台表单中显示的字段
    search_fields = ['user', 'course']  # 查询字段
    list_filter = ['user', 'course', 'add_time']  # 过滤字段
# 将后台管理器与models进行关联注册。
xadmin.site.register(UserCourse, UserCourseAdmin)
```
#### 2. 对xadmin后台页面显示
```
import xadmin
from xadmin import views

# 创建xadmin的最基本管理器配置，并与view绑定
class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    use_bootswatch = True


# 全局修改，固定写法
class GlobalSettings(object):
    # 修改title
    site_title = 'NBA后台管理界面'
    # 修改footer
    site_footer = '科比的公司'
    # 收起菜单
    menu_style = 'accordion'


# 将基本配置管理与view绑定
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 将title和footer信息进行注册
xadmin.site.register(views.CommAdminView, GlobalSettings)
```
#### 3. 后台向表里添加一条数据时关联添加其他数据，同时修改某些字段
```
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
```

### view
#### 1. 以函数形式, 不建议使用
```
def user_login(request):
    if request.method == 'POST':
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
    elif request.method == 'GET':
        return render(request, 'login.html')
```
#### 2. 以类形式，需要继承View，建议使用
```
from django.views import View
from django.contrib.auth import authenticate, login, logout


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
```
#### 3. 多种登陆方式，用户名邮箱;需要继承ModelBackend并复写authenticate()方法。同时需要再setting里设置
```
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

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
```
#### 4. 使用django自带的login()
```
# 登录, request和user必传
login(request, user)
```
#### 5. 使用django自带的logout()
```
class LogoutView(View):
    """用户登出"""

    def get(self, request):
        # request必传
        logout(request)
        return HttpResponseRedirect(reverse('index'))
```
#### 6. 使用django自带的加密make_password
```
from django.contrib.auth.hashers import make_password

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
```
#### 7. 跳转到路由
```
from django.urls import reverse
return HttpResponseRedirect(reverse('index'))
```
#### 8. 第三方分页模块
```
首先需要在setting中配置
INSTALLED_APPS =（
    ...
    'pure_pagination'，
）

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}


from pure_pagination import Paginator, PageNotAnInteger

all_messages = UserMessage.objects.filter(user=request.user.id)
# 分页
try:
    page = request.GET.get('page', 1)
except PageNotAnInteger:
    page = 1
p = Paginator(all_messages, 6, request=request)
messages = p.page(page)

在前端页面显示
<ul class="pagelist">
    {% if messages.has_previous %}
        <li class="long"><a href="?{{ messages.previous_page_number.querystring }}">上一页</a></li>
    {% endif %}

    {% for page in messages.pages %}
        {% if page %}
            {% ifequal page messages.number %}
                <li class="active"><a href="?{{ page.querystring }}">{{ page }}</a></li>
            {% else %}
                <li><a href="?{{ page.querystring }}" class="page">{{ page }}</a></li>
            {% endifequal %}
        {% else %}
            <li class="none"><a href="">...</a></li>
        {% endif %}
    {% endfor %}
    {% if messages.has_next %}
        <li class="long"><a href="?{{ messages.next_page_number.querystring }}">下一页</a></li>
    {% endif %}
</ul>
```
#### 9. 没有跳转到登陆界面,使用django的login_required
```
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        
views.py中的类继承它
```
#### 10. 使用django自带的函数判断用户是否登陆
request.user.is_authenticated()  # 返回True或者False



### 发邮件
#### 1. 使用django自带的函数发送邮件
```
首先在setting中配置邮件相关信息

from django.core.mail import send_mail

# 使用Django内置函数完成邮件发送。四个参数：主题，邮件内容，从哪里发，接受者list
send_status = send_mail(email_title, email_body, EMAIL_HOST_USER, [email])
```

### template 继承
#### 1. 






