# -*- coding: utf8 -*-
from django.core.exceptions import ValidationError
from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from . import models

class LoginForm(forms.Form):
    username = fields.CharField(
        # required=True,
        # widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '用户名为8-12个字符'}),
        # min_length=6,
        # max_length=12,
        # strip=True,
        # error_messages={'required': '标题不能为空',
        #                 'min_length': '用户名最少为6个字符',
        #                 'max_length': '用户名最不超过为20个字符'},
    )


    password = fields.CharField(
        # required=True,
        # widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码，必须包含数字,字母,特殊字符'},render_value=True),
        # min_length=6,
        # max_length=12,
        # strip=True,
        # validators=[
        #     # 下面的正则内容一目了然，我就不注释了
        #     RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
        #     RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
        #     RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
        #     #RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
        # ], #用于对密码的正则验证
        # error_messages={'required': '密码不能为空!',
        #                 'min_length': '密码最少为6个字符',
        #                 'max_length': '密码最多不超过为12个字符!',},
    )

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


# class loginForm(forms.Form):
#     username = fields.CharField(
#         required=True,
#         widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '请输入用户名'}),
#         min_length=6,
#         max_length=12,
#         strip=True,
#         error_messages={'required': '用户名不能为空',}
#     )

#     password = fields.CharField(
#         widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码'}),
#         required=True,
#         min_length=6,
#         max_length=12,
#         strip=True,
#         error_messages={'required': '密码不能为空!',}
#     )

#     def clean(self):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = models.User.objects.filter(username=username).first()
#         if username and password:
#             if not user:
#                 # self.error_dict['password_again'] = '两次密码不匹配'
#                 raise ValidationError('用户名不存在！')
#             elif password != user.password:
#                 raise ValidationError('密码不正确')
