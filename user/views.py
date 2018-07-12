from django.template import loader
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from django.shortcuts import render,redirect,HttpResponse
from io import BytesIO
from .models import User	
from . import registerForm
from . import loginForm
import datetime
import uuid
from django.core.validators import validate_email



def login(request):
	# print(request.POST)
	if request.session.get('log_in') != None:
		form = loginForm.LoginForm()
		return render(request,'login.html',{'form':form,'message':'登录:'+request.session['username']})

	if request.method == 'GET':
		form = loginForm.LoginForm()
		# print('GET')
		return render(request,'login.html',{'form':form})

	elif request.method == 'POST':
		# print(request.POST)
		form = loginForm.LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			session_uuid = str(uuid.uuid1())
			request.session['username'] = username
			request.session['login'] = True
			request.session.set_expiry(60*60*24)  # sesson 1天后过期
			return render(request,'login.html',{'form':form,'message':'登录'+request.session['username']})



def register(request):
	if request.method =='GET':
		request.session.flush()
		t = loader.get_template('register.html')
		form = registerForm.RegisterForm()
		c ={'message' :'hiahiahiahiahiahiahia','form':form}
		return HttpResponse(t.render(c,request))

	if request.method == 'POST':
		request.session.flush()
		form = registerForm.RegisterForm(request.POST) 
		if form.is_valid():
			user = User()
			user.username = form.cleaned_data.get('username')
			user.password = form.cleaned_data.get('password_1')
			user.cellphone = form.cleaned_data.get('cellphone')
			user.email = form.cleaned_data.get('email')
			user.user_guid = str(uuid.uuid1())
			user.account_type = 'plastic'
			user.save()
			# return HttpResponse(user.instr())
			t = loader.get_template('login.html')
			loginform = loginForm.LoginForm()
			c ={'message' :'注册成功，请重新登录','form':loginform}
			return HttpResponse(t.render(c,request))
		else:
			# error = form.errors
			# return HttpResponse(form.username)
			t = loader.get_template('register.html')
			# form = registerForm.RegisterForm()
			c ={'messgage' :'请重新填写资料','form':form}
			return HttpResponse(t.render(c,request))

def logout(request):
	if request.method == 'POST' or request.method == 'GET':
		request.session.flush()
		form = loginForm.LoginForm()
		return render(request,'login.html',{'form':form,'message':'已注销，请重新登录'})



