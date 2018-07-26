# -*- coding: utf8 -*-
from django.core.exceptions import ValidationError
from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from . import models


# 用户注册form
class RegisterForm(forms.Form):
	username = fields.CharField(
		required=True,
		widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '用户名为8-12个字符'}),
		min_length=6,
		max_length=12,
		strip=True,
		error_messages={'required': '标题不能为空',
						'min_length': '用户名最少为6个字符',
						'max_length': '用户名最不超过为20个字符'},
	)
	email = fields.EmailField(
		required=True,
		widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '请输入邮箱'}),
		# strip=True,
		error_messages={'required': '邮箱不能为空',
						'invalid':'请输入正确的邮箱格式'},
	)

	cellphone = fields.CharField(
		required=True,
		widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '请输入电话'}),
		strip=True,
		error_messages={'required': '电话号码不能为空',
						'invalid':'请输入正确的电话格式'},
	)

	password_1 = fields.CharField(
		required=True,
		widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码，必须包含数字,字母,特殊字符'},render_value=True),
		min_length=6,
		max_length=12,
		strip=True,
		validators=[
			# 下面的正则内容一目了然，我就不注释了
			RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
			RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
			RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
			#RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
		], #用于对密码的正则验证
		error_messages={'required': '密码不能为空!',
						'min_length': '密码最少为6个字符',
						'max_length': '密码最多不超过为12个字符!',},
	)
	password_2 = fields.CharField(
		required=True,
		# render_value会对于PasswordInput，错误是否清空密码输入框内容，默认为清除，我改为不清楚
		widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请再次输入密码!'},render_value=True),
		strip=True,
		error_messages={'required': '请再次输入密码!',}

	)

	def clean_username(self):
		# 查找用户是否已经存在
		username = self.cleaned_data.get('username')
		users = models.User.objects.filter(username=username).count()
		if users:
			raise ValidationError('用户已经存在！')
		return username

	def clean_email(self):
		# 查找用户是否已经存在
		email = self.cleaned_data.get('email')
		email_count = models.User.objects.filter(email=email).count() #从数据库中查找是否用户已经存在
		if email_count:
			raise ValidationError('该邮箱已经注册！')
		return email

	def _clean_password_2(self): #查看两次密码是否一致
		password1 = self.cleaned_data.get('password_1')
		password2 = self.cleaned_data.get('password_2')
		if password1 and password2:
			if password1 != password2:
				# self.error_dict['password_again'] = '两次密码不匹配'
				raise ValidationError('两次密码不匹配！')

	def clean(self):
		self._clean_password_2() 



# 用户登录form
class LoginForm(forms.Form):
	username = fields.CharField()
	password = fields.CharField()

	def clean_username(self):
		# 查找用户是否已经存在
		username = self.cleaned_data.get('username')
		# try:
		#	 users = models.User.objects.filter(username=username).count()
		# 	return username
		# except models.User.objects.filter(username=username).count()DoesNotExist:
		# 	raise ValidationError('用户名不存在')
		users = models.User.objects.filter(username=username).count()
		if users:
			return username
		else:
			raise ValidationError('用户名不存在')
		

	def clean_password(self): 
		#查看两次密码是否一致
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		# user = models.User.objects.get(username=username)
		try:
			user = models.User.objects.get(username=username)
			if user.password != password:
				raise ValidationError('密码错误')
			return password
		except:
			raise ValidationError('用户名都错了，我当然不会告诉你密码是不是对的')

	def clean(self):
		# self.clean_password()
		self.clean_username()






# 用户重置密码form
class ResetByUsernameForm(forms.Form):
	username = fields.CharField(
		required=True,
		widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '请输入用户名'}),
		min_length=6,
		max_length=12,
		strip=True,
		error_messages={'required': '用户名不能为空',}
	)


	old_password = fields.CharField(
		widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码'}),
		required=True,
		min_length=6,
		max_length=12,
		strip=True,
		error_messages={'required': '密码不能为空!',}
	)
	new_password_1 = fields.CharField(
		required=True,
		widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码，必须包含数字,字母,特殊字符'},render_value=True),
		min_length=6,
		max_length=12,
		strip=True,
		validators=[
			# 下面的正则内容一目了然，我就不注释了
			RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
			RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
			RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
			#RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
		], #用于对密码的正则验证
		error_messages={'required': '密码不能为空!',
						'min_length': '密码最少为6个字符',
						'max_length': '密码最多不超过为12个字符!',},
	)
	new_password_2 = fields.CharField(
		required=True,
		widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码，必须包含数字,字母,特殊字符'},render_value=True),
		min_length=6,
		max_length=12,
		strip=True,
		validators=[
			# 下面的正则内容一目了然，我就不注释了
			RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
			RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
			RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
			#RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
		], #用于对密码的正则验证
		error_messages={'required': '密码不能为空!',
						'min_length': '密码最少为6个字符',
						'max_length': '密码最多不超过为12个字符!',},
	)

	
	def clean_username(self):
		username = self.cleaned_data.get('username')
		users = models.User.objects.filter(username=username).count()
		if not users:
			raise ValidationError('用户名不存在')
		return username

	def clean_old_password(self): #查看两次密码是否一致
		username = self.cleaned_data.get('username')
		old_password = self.cleaned_data.get('old_password')
		user = models.User.objects.get(username=username)
		if user.password != old_password:
			raise ValidationError('旧密码不正确')
		return old_password
	def clean_new_password_2(self): #查看两次密码是否一致
		new_password_1 = self.cleaned_data.get('new_password_1')
		new_password_2 = self.cleaned_data.get('new_password_2')
		# print('pwd2: '+new_password_2)
		# print('pwd1: '+new_password_1)
		if new_password_1 and new_password_2:
			if new_password_1 != new_password_2:
				# self.error_dict['password_again'] = '两次密码不匹配'
				raise ValidationError('两次密码不匹配！')

	#def clean(self):
		#self.clean_username()
		#self.clean_old_password()
		# self.clean_new_password_2()








