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
import PyPDF2
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from django.db.models import Q
import os, shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 登录,DONE
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
			request.session['user_guid'] = str(User.objects.filter(username=username)[0].user_guid)
			request.session['login'] = True
			request.session.set_expiry(60*60*24)  # sesson 1天后过期
			
			return HttpResponseRedirect('/user/main/')
		return HttpResponse(t.render(c,request))


# 注册,DONE
def register(request):
	print('register')
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
			user.account_type = 'plastic'
			user.save()
			print(user.instr())
			t = loader.get_template('login.html')
			loginform = LoginForm()
			c ={'message' :'注册成功，请重新登录','form':loginform}
			return HttpResponse(t.render(c,request))
		else:

			t = loader.get_template('register.html')
			c ={'messgage' :'请重新填写资料','form':form}
			return HttpResponse(t.render(c,request))

# 注销,DONE
def logout(request):
	if request.method == 'POST' or request.method == 'GET':
		request.session.flush()
		form = LoginForm()
		return render(request,'login.html',{'form':form,'message':'已注销，请重新登录'})

#修改密码,DONE
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
	c = {}
	if request.method =='POST':
		if not request.POST.get('username'):
			c['message'] = '请登录'
		if request.POST.get('file_guid') != None:
			# print(request.POST.get('file_guid'))
			# print(request.POST.get('file_guid'))
			login_user = User.objects.filter(username=request.session.get('username'))[0]	
			delete_file_guid = request.POST.get('file_guid')
			delete_file = File.objects.filter(file_guid = delete_file_guid)[0]
			if delete_file.owner != login_user:
				c['message'] = 'あなたはわたしのマスタか？'
				return JsonResponse(c)
			delete_file_path = delete_file.path
			delete_dir_path = '/'.join(delete_file_path.split('/')[:-1])
			print('path:'+delete_dir_path)
			if os.path.exists(delete_dir_path):  
				shutil.rmtree(delete_dir_path)
			# file表中删除
			File.objects.filter(file_guid = delete_file_guid).delete()
			# share表中删除（cascade)///
			# t = loader.get_template('file_management.html')
			# files = File.objects.all()
			# c ={'files':files}
			c['message'] = 'success'
	return JsonResponse(c)



@ensure_csrf_cookie
@csrf_exempt
def share_file(request):
	print(request.POST)
	#正确的输入
	correct_co_editors = []
	#错误的输入，提示用户输错了
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
		if not owner:
			return HttpResponse('请登录')
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
				share.share_user= matched_co_editors
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








@csrf_exempt
def upload(request):
	c ={}  #return message
	t = loader.get_template('main.html')
	if request.method == 'POST':# 获取对象
		obj = request.FILES.get('file')
		filename = obj.name	#filename
		username = request.session.get('username') #username
		file_dir = '' # full path of the file
		
		
		user = User.objects.filter(username=username)[0] if request.session.get('login') else None
		# print(filename +'\t' + username)
		
		if File.objects.filter(filename=filename).filter(owner=user).count():
			c['message']='已存在同名文件，请先修改文件名后上传'
			return JsonResponse(c)
		if request.session.get('login'):
			file_dir = BASE_DIR +'/files/'+username+'/'+filename+'/'
		else:
			file_dir = BASE_DIR +'/files/temp/'+username+'/'+filename+'/'
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
		with open(file_dir+filename,'wb') as f:
			for chunk in obj.chunks():
				f.write(chunk)
		if os.path.exists(file_dir+filename):
			c['message']='success'
			file =File()
			file.owner = User.objects.filter(username=username)[0]
			file.file_guid = str(uuid.uuid1())
			file.filename = filename
			file.path = file_dir+filename
			total_page = file.total_page = get_total_page(file_dir+filename)
			file.save()
			convert_next_10(file.path,1,total_page)
		else:
			c['message']='上传失败'
			return JsonResponse(c)
	return JsonResponse(c)

def get_total_page(file_path):
	f= PyPDF2.PdfFileReader(file_path)
	return f.getNumPages()



def file_management(request):
	t = loader.get_template('file_management.html')
	user = User.objects.filter(username=request.session.get('username'))[0]
	files = File.objects.filter(owner = user)
	shares = Share.objects.filter(share_user=user);
	# print(shares[0].shared_file)
	# print(files)
	c ={'messgage':user.username, 'files':files,'shares':shares}
	return HttpResponse(t.render(c,request))


def convert_next_10(file_path,start_page,total_page):
	for i in range(start_page,min(start_page+10,total_page+1)):
		# <filename> <page> <zoom> <degree> <output filename> <needle>
		img_path = '/'.join(file_path.split('/')[:-1]) +'/'+str(i)+'.png'
		cmd = 'python3 %s %s %s %s %s %s %s' %(BASE_DIR+'/user/static/scripts/convert_to_img.py',file_path, str(i), '400','0',img_path,'1')
		print(cmd)
		os.popen(cmd,'w')

def test(request):
	print(BASE_DIR)
	return HttpResponse('123')


