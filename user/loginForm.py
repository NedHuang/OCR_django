# -*- coding: utf8 -*-
from django.core.exceptions import ValidationError
from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from . import models

class LoginForm(forms.Form):
    username = fields.CharField()

    password = fields.CharField()

    def clean_username(self):
        # 对username的扩展验证，查找用户是否已经存在
        username = self.cleaned_data.get('username')
        users = models.User.objects.filter(username=username).count()
        if not users:
            raise ValidationError('用户名不存在')
        return username

    def clean_password(self): #查看两次密码是否一致
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = models.User.objects.get(username=username)
        if user.password != password:
            raise ValidationError('密码错误')
        return password

    def clean(self):
        #是基于form对象的验证，字段全部验证通过会调用clean函数进行验证
        self.clean_password() #简单的调用而已



