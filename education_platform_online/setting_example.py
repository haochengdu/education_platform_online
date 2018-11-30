#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time    : 18-11-30 下午5:42
@Author  : TX
@File    : setting_example.py
@Software: PyCharm
"""
"""
Django settings for education_platform_online project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '44qp_3uj%x&!-2w!bm%y*rp5th6aa%6g$2+u^&x6mqtla9zzn@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
# 设置自定义的验证类
AUTHENTICATION_BACKENDS = (
    'users.views.CustomBackend',
)
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pure_pagination',
    'users',
    'course',
    'organization',
    'operation',
    'xadmin',
    'DjangoUeditor',
    'crispy_forms',
    'captcha',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'education_platform_online.urls'

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

WSGI_APPLICATION = 'education_platform_online.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mxonline',  # 数据库名字
        'USER': 'root',  # 账号
        'PASSWORD': 'mysql',  # 密码
        'HOST': '127.0.0.1',  # IP
        'PORT': '3306',  # 端口
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

AUTH_USER_MODEL = 'users.UserProfile'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# 静态文件 当DEBUG = False(生产模式下)时需要重新配置静态文件
# 404和500,生成环境汇总，必须设置debug = False
# 一旦debug改为false，django就不会代管你的静态文件，所以要设置一个url处理静态文件
STATIC_ROOT = os.path.join(BASE_DIR, '/static/')

# 设置上传文件的路径
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 指定根目录

# 使用新浪邮箱发邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sina.cn'
EMAIL_PORT = 25
# EMAIL_HOST_USER = '新浪邮箱账号@sina.cn'
EMAIL_HOST_USER = '1xxxxxxxxxxxxm@sina.cn'
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxx'
# 注册有效期天数
CONFIRM_DAYS = 7
