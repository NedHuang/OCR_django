from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from django.shortcuts import render,redirect,HttpResponse
from io import BytesIO
from .models import User
from .models import File
from .forms import RegisterForm,LoginForm,ResetByUsernameForm
import datetime
import uuid
from django.core.validators import validate_email
import os
import PyPDF2
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 登录
def login(request):
	# print(request.POST)
	if request.session.get('log_in') != None:
		form = LoginForm()
		return render(request,'login.html',{'form':form,'message':'登录:'+request.session['username']})

	if request.method == 'GET':
		form = LoginForm()
		# print('GET')
		return render(request,'login.html',{'form':form})

	elif request.method == 'POST':
		form = LoginForm(request.POST)
		t = loader.get_template('login.html')
		c ={'messgage' :'请重新填写资料','form':form}
		username =''
		password =''
		
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			session_uuid = str(uuid.uuid1())
			request.session['username'] = username
			request.session['login'] = True
			request.session.set_expiry(60*60*24)  # sesson 1天后过期
			
			return HttpResponseRedirect('/user/main/')
		return HttpResponse(t.render(c,request))

def anonymous(request):
	user = User()
	username_and_guid = str(uuid.uuid1())
	user.username = username_and_guid
	user.user_guid = username_and_guid
	user.account_type = 'temp'
	user.save()
	request.session.flush()
	request.session['login'] = False
	request.session['username'] = username_and_guid
	return HttpResponseRedirect('/user/main/')


# 注册
def register(request):
	if request.method =='GET':
		request.session.flush()
		t = loader.get_template('register.html')
		form = RegisterForm()
		c ={'message' :'hiahiahiahiahiahiahia','form':form}
		return HttpResponse(t.render(c,request))

	if request.method == 'POST':
		request.session.flush()
		form = RegisterForm(request.POST) 
		if form.is_valid():
			user = User()
			user.username = form.cleaned_data.get('username')
			user.password = form.cleaned_data.get('password_1')
			user.cellphone = form.cleaned_data.get('cellphone')
			user.email = form.cleaned_data.get('email')
			user.user_guid = str(uuid.uuid1())
			user.account_type = 'plastic'
			user.save()

			t = loader.get_template('login.html')
			loginform = LoginForm()
			c ={'message' :'注册成功，请重新登录','form':loginform}
			return HttpResponse(t.render(c,request))
		else:

			t = loader.get_template('register.html')
			c ={'messgage' :'请重新填写资料','form':form}
			return HttpResponse(t.render(c,request))

# 注销
def logout(request):
	if request.method == 'POST' or request.method == 'GET':
		request.session.flush()
		form = LoginForm()
		return render(request,'login.html',{'form':form,'message':'已注销，请重新登录'})

#修改密码
def resetByUsernameForm(request):
	if request.method =='GET':
		request.session.flush()
		t = loader.get_template('resetByUsernameForm.html')
		form = ResetByUsernameForm()
		c ={'message' :'resetByUsernameForm','form':form}
		return HttpResponse(t.render(c,request))
		# return HttpResponse('get')
	if request.method == 'POST':
		#request.session.flush()
		form = ResetByUsernameForm(request.POST)
		print(form)
		if form.is_valid():
			password = form.cleaned_data.get('new_password_1')
			username = form.cleaned_data.get('username')

			User.objects.filter(username=username).update(password=password)
			t = loader.get_template('resetByUsernameForm.html')
			c ={'message' :'修改成功','form':form}
			return HttpResponse(t.render(c,request))
		else:

			t = loader.get_template('resetByUsernameForm.html')
			c ={'message' :'请重新填写','form':form}
			return HttpResponse(t.render(c,request))












@ensure_csrf_cookie
@csrf_exempt
def main(request):
	if request.method =='POST':
		print(request.POST.get('data'))
		return HttpResponse(request.POST.get('data'))
	return render(request,'main.html',{'message':'message'+request.session['username']})

def ajax(request):
	if request.method =='POST':
		if request.POST.get('operation') =='test':
			print(request.POST.get('data'))
			return HttpResponse(request.POST.get('data'))

def upload(request):
	t = loader.get_template('main.html')
	if request.method == 'POST':# 获取对象
		obj = request.FILES.get('myfile')
		filename = obj.name
		username = request.session.get('username')
		print(filename +'\t' + username)
		c ={}
		if request.session.get('log_in'):
			file_dir = BASE_DIR +'/files/'+username+'/'+filename+'/'
		else:
			file_dir = BASE_DIR +'/files/temp/'+username+'/'+filename+'/'
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
		with open(file_dir+filename,'wb') as f:
			for chunk in obj.chunks():
				f.write(chunk)
		if os.path.exists(file_dir+filename):
			c['messgage']='上传成功'
			file =File()
			file.owner = User.objects.filter(username=username)[0]
			file.file_guid = str(uuid.uuid1())
			file.filename = filename
			file.path = file_dir+filename
			file.save()
		else:
			c['messgage']='上传失败'

	return HttpResponse(t.render(c,request))

def get_total_page(file_path):
	f= PyPDF2.PdfFileReader(file_path)
	return f.getNumPages()







def file_management(request):
	t = loader.get_template('file_management.html')
	files = File.objects.all()
	c ={'files':files}
	return HttpResponse(t.render(c,request))







	 
