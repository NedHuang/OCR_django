from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from django.shortcuts import render,redirect,HttpResponse
from io import BytesIO
from .models import User,File,Object,Share,Group,UserGroup
from .forms import RegisterForm,LoginForm,ResetByUsernameForm
import datetime
import uuid
from django.core.validators import validate_email
import os
import PyPDF2
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from django.db.models import Q


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
			request.session['user_guid'] = User.objects.filter(username=username)[0].user_guid
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

# 根据post的action字段来执行不同function
def ajax(request):
	if request.method =='POST':
		if request.POST.get('action') =='test':
			print(request.POST.get('data'))
			return HttpResponse(request.POST.get('data'))
		# if request.POST.get('action') =='delete_file':
		# 	return delete_file(request)


@ensure_csrf_cookie
@csrf_exempt
def delete_file(request):
	print(request.POST)
	if request.method =='POST':
		if request.POST.get('file_guid') != None:
			print(request.POST.get('file_guid'))
			delete_file_guid = request.POST.get('file_guid')
			delete_file_path = File.objects.filter(file_guid = delete_file_guid)[0].path
			print('path:'+delete_file_path)
			if os.path.exists(delete_file_path):  
   	 			os.remove(delete_file_path)
			# file表中删除
			File.objects.filter(file_guid = delete_file_guid).delete()
			# share表中删除（cascade)///

			t = loader.get_template('file_management.html')
			files = File.objects.all()
			c ={'files':files}
	return HttpResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def share_file(request):
	print(request.POST)
	#正确的用户名
	correct_co_editors = []
	#错误的用户名
	wrong_input = []
	matched_co_editors = None
	shared_file = None
	if request.method == 'POST':
		owner_guid = request.session.get('user_guid')
		file_guid = request.POST.get('file_guid')
		co_editors = request.POST.get('co_editors').split('\n')
		if File.objects.filter(file_guid = file_guid).exists():
			print('file exists')
			shared_file = File.objects.filter(file_guid = request.POST.get('file_guid'))[0]

		owner = User.objects.filter(user_guid = request.session.get('user_guid'))[0]
		
		print('file_guid: ' + shared_file.file_guid)
		print( 'co_editors: '+str(co_editors))
		print('owner_guid: ' + str(owner_guid))
		print('ownser_username: '+owner.username)

		if not owner:
			return HttpResponse('failed to share')
		for i in co_editors: # i是输入的字段（用户名或者邮箱）
			# 只会match到一个，除非A的用户名叫xxx@yyy.com,B的邮箱也是xxx@yyy.com, 在注册时检查一下？
			if User.objects.filter(Q(username=i) | Q(email=i)).exists():
				matched_co_editors = User.objects.filter(Q(username=i) | Q(email=i))[0]
				# print('matched_co_editors: ' + matched_co_editors.username)
			else:
				matched_co_editors = None
			if matched_co_editors:
				correct_co_editors.append(matched_co_editors.username)
				share = Share()
				share.owner = owner
				share.share_user_guid = matched_co_editors.user_guid
				share.shared_file = shared_file
				share.permission = 'share'
				share.save()
				print('matched_co_editors: ' + matched_co_editors.username)
				print(shared_file.filename)
				print(owner.username)
			else:
				wrong_input.append(i)
	response_data = {}
	response_data['correct_co_editors']= correct_co_editors
	response_data['wrong_input']=wrong_input
	return JsonResponse(response_data)









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
	username = request.session.get('username')
	user = User.objects.filter(username=username)[0]
	files = File.objects.filter(owner = user)
	share = Share.objects.filter(share_user_guid = request.session.get('user_guid'))
	c ={'files':files,'shares':share,}
	print(files)
	return HttpResponse(t.render(c,request))







	 
