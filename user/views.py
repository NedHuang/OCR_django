 # -*- coding: utf-8 -*-
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse,StreamingHttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields, widgets
from django.core.validators import RegexValidator
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import escape_uri_path
from io import BytesIO
from .models import User,File,Object,Share,Group,GroupMember
from .forms import RegisterForm,LoginForm,ResetByUsernameForm
import datetime
import uuid
from django.core.validators import validate_email
import PyPDF2
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from django.db.models import Q
import os, shutil, tarfile, zipfile
import time
from PIL import Image


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 登录,DONE
def login(request):
	# print(request.POST)
	if request.session.get('login') != None:
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
			print(user)
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



#删除某个文件, request 发送文件的guid。然后找出file,删除数据库记录以及文件夹下所有文件
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
			#不是文件的所有者，弹出错误提示
			if delete_file.owner != login_user:
				c['message'] = 'あなたはわたしのマスタか？'
				return JsonResponse(c)
			delete_file_path = delete_file.path
			# 文件所在的文件夹，连通png文件以及txt文件一并删除
			delete_dir_path = '/'.join(delete_file_path.split('/')[:-1])
			print('path:'+delete_dir_path)
			if os.path.exists(delete_dir_path):  
				shutil.rmtree(delete_dir_path)
			File.objects.filter(file_guid = delete_file_guid).delete()
			c['message'] = 'success'
	return JsonResponse(c)


#分享文件给某个用户
@ensure_csrf_cookie
@csrf_exempt
def share_file(request):
	print(request.POST)
	response_data = {}
	#正确的输入
	correct_co_editors = []
	#错误的输入，提示用户输错了
	wrong_input = []
	already_shared = []
	matched_co_editors = None
	shared_file = None
	#获取owner,file的UUID和要分享的用户名
	if request.method == 'POST':
		owner_guid = request.session.get('user_guid')
		file_guid = request.POST.get('file_guid')
		co_editors = request.POST.get('co_editors').split('\n')
		if File.objects.filter(file_guid = file_guid).exists():
			print('file exists')
			shared_file = File.objects.filter(file_guid = request.POST.get('file_guid'))[0]
		owner = User.objects.filter(user_guid = request.session.get('user_guid'))[0]
		# 请登录。。。。
		if not owner:
			return HttpResponse('请登录')
		for i in co_editors: # i是输入的字段（用户名或者邮箱）
			# 只会match到一个，除非A的用户名叫xxx@yyy.com,B的邮箱也是xxx@yyy.com, 在注册时检查一下？
			if User.objects.filter(Q(username=i) | Q(email=i)).exists():
				matched_co_editors = User.objects.filter(Q(username=i) | Q(email=i))[0]
				# print('matched_co_editors: ' + matched_co_editors.username)
			else:
				matched_co_editors = None
			#避免重复分享：
			if Share.objects.filter(share_user = matched_co_editors).filter(shared_file = shared_file).count():
				already_shared.append(matched_co_editors.username)
			#如果分享对象
			elif matched_co_editors:
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
	
	response_data['correct_co_editors']= correct_co_editors
	response_data['wrong_input']=wrong_input
	response_data['already_shared']=already_shared
	return JsonResponse(response_data)


@csrf_exempt
def upload(request):

	c ={}  #return message
	t = loader.get_template('main.html')
	if request.method == 'POST':# 获取对象
		obj = request.FILES.get('file')
		filename = obj.name	#filename
		if ' ' in filename:
			filename = filename.replace(' ','_')
		username = request.session.get('username') #username
		file_dir = '' # full path of the file
		user = User.objects.filter(username=username)[0] if request.session.get('login') else None
		# print(filename +'\t' + username)
		
		if File.objects.filter(filename=filename).filter(owner=user).count():
			c['message']='已存在同名文件，请先修改文件名后上传'
			return JsonResponse(c)
		if request.session.get('login'):
			file_dir = BASE_DIR +'/user/static/files/'+username+'/'+filename+'/'
		else:
			file_dir = BASE_DIR +'/user/static/files/temp/'+username+'/'+filename+'/'
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
			if not request.session['resolution']:
				request.session['resolution'] = '400' 
			# convert_next_10(request,file.path,1,total_page)
		else:
			c['message']='上传失败'
			return JsonResponse(c)
	return JsonResponse(c)

def get_total_page(file_path):
	f= PyPDF2.PdfFileReader(file_path)
	return f.getNumPages()



def file_management(request):
	if (not request.session.get('username')) or (not request.session.get('login')):
		# form = LoginForm()
		# return render(request,'login.html',{'form':form})
		return login(request)
	t = loader.get_template('file_management.html')
	print(request.session.get('username'))
	user = User.objects.filter(username=request.session.get('username'))[0]
	files = File.objects.filter(owner = user)
	shares = Share.objects.filter(share_user=user);
	c ={'messgage':request.session.get('username'), 'files':files,'shares':shares}
	return HttpResponse(t.render(c,request))


def convert_next_10(request,file_path,start_page,total_page):
	for i in range(start_page,min(start_page+10,total_page+1)):
		# <filename> <page> <zoom> <degree> <output filename> <needle>
		img_path = '/'.join(file_path.split('/')[:-1]) +'/'+str(i)+'.png'
		cmd = 'python3 %s %s %s %s %s %s %s' %(BASE_DIR+'/user/static/scripts/convert_to_img.py',file_path, str(i), request.session['resolution'],'0',img_path,'1')
		print(cmd)
		os.popen(cmd,'w')


@ensure_csrf_cookie
@csrf_exempt
# this is the start when you edit the file, it will assign all session vars
def edit_file(request):
	file_guid = request.POST.get('file_guid')
	print('loadfile: ' + file_guid)
	file = File.objects.filter(file_guid=request.POST.get('file_guid'))[0]
	# 为了记录最后访问此文件的时间
	file.save()
	user = User.objects.filter(username=request.session.get('username'))[0]
	c = {}
	t=loader.get_template('main.html')
	
	request.session['file_guid'] = str(file_guid)
	request.session['total_page'] = file.total_page
	request.session['page'] = page =1
	request.session['path'] = file.path
	request.session['owner_guid'] = str(file.owner.user_guid)
	request.session['filename'] = file.filename
	check_and_convert(request,page)
	size = request.session['size'] = get_image_size(request,page)
	c['image_width'] =size[0]
	c['image_height'] =size[1]
	c['owner_guid'] = request.session['owner_guid']
	c['message'] = file.filename
	c['filename'] = request.session['filename']
	c['last_modified'] = str(file.last_modified)
	c['path'] = str(file.path)
	c['page'] = 1
	c['username'] = request.session['username']
	c['total_page'] = request.session.get('total_page')
	print('edit_file')
	print(c)
	return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def load_file(request):
	user = User.objects.filter(username = request.session['username'])[0] if User.objects.filter(username = request.session['username']).count() else None
	request.session['resolution'] = str(400)
	page = request.session['page'] = 1;
	file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	path = file.path
	print('+++++++++++++++++++++')
	check_and_convert(request,page)
	print('---------------------')
	c = {}
	check_and_convert(request,page)
	size = request.session['size'] = get_image_size(request,page)
	c['image_width'] =size[0]
	c['image_height'] =size[1]
	c['page'] = page
	c['total_page'] = request.session.get('total_page')
	c['filename'] = request.session['filename']
	c['username'] = user.username
	c['user_email'] = user.email
	c['file_guid'] = request.session['file_guid']
	c['img_url'] ='/'.join(path.split('/')[:-1]).split('/static/')[-1]+'/'+str(page)+'.png'
	c['owner_guid'] =request.session['owner_guid']= str(file.owner.user_guid)
	c['resolution'] = request.session['resolution']
	t=loader.get_template('main.html')

	print(c)
	return HttpResponse(t.render(c,request))

@ensure_csrf_cookie
@csrf_exempt
def next_page(request):
	page = request.session['page']
	total_page = request.session['total_page']
	c={}
	if page < total_page:
		print( 'page < total_page')
		page = page + 1
		c['page'] = page
		request.session['page'] = page
		path = request.session['path']
		check_and_convert(request,page)
		size = request.session['size'] = get_image_size(request,page)
		c['image_width'] =size[0]
		c['image_height'] =size[1]
		# 	# 在此处添加调用POD的cmd,并且执行
		c['status'] = 'success'
		c['img_url'] = '/'.join(path.split('/')[:-1]).split('/static/')[-1]+'/'+str(page)+'.png'
		c['page'] = page
		c['total_page'] = request.session['total_page']
		c['username'] = request.session.get('username')
		c['owner_guid'] = request.session['owner_guid']
		print('page: '+str(request.session['page']))
		return JsonResponse(c)
	else:
		c['page'] = page
		c['total_page'] = request.session['total_page']
		c['status'] ='first_page'
		c['username'] = request.session.get('username')
		return JsonResponse(c)

@csrf_exempt
def prev_page(request):
	page = request.session['page']
	total_page = request.session['total_page']
	c={}
	if page > 1:
		print( 'page > 1')
		page = page -1
		c['page'] = page
		request.session['page'] = page
		path = request.session['path']
		check_and_convert(request,page)
		size = request.session['size'] = get_image_size(request,page)
		c['image_width'] =size[0]
		c['image_height'] =size[1]
			# 在此处添加调用POD的cmd,并且执行
		c['status'] = 'success'
		c['img_url'] = '/'.join(path.split('/')[:-1]).split('/static/')[-1]+'/'+str(page)+'.png'
		c['total_page'] = request.session['total_page']
		c['username'] = request.session.get('username')
		c['page'] = page
		c['owner_guid'] = request.session['owner_guid']
		print('page: '+str(request.session['page']))
		return JsonResponse(c)
	else:
		c['page'] = page
		c['total_page'] = request.session['total_page']
		c['status'] ='first_page'
		c['username'] = request.session.get('username')
		return JsonResponse(c)



@csrf_exempt
def last_page(request):
	c={}
	request.session['page'] = page = request.session['total_page']
	path = request.session['path']
	last_path= '/'.join(path.split('/')[:-1])+'/'+str(page)+'.png'
	check_and_convert(request,page)
	size = request.session['size'] = get_image_size(request,page)
	c['image_width'] =size[0]
	c['image_height'] =size[1]
	c['status'] = 'success'
	c['img_url'] = '/'.join(path.split('/')[:-1]).split('/static/')[-1]+'/'+str(page)+'.png'
	c['total_page'] = request.session['total_page']
	c['username'] = request.session.get('username')
	c['page'] = page
	c['owner_guid'] = request.session['owner_guid']
	print('page: '+str(request.session['page']))
	return JsonResponse(c)
	


@csrf_exempt
def first_page(request):
	c={}
	request.session['page'] = page = 1
	path = request.session['path']
	check_and_convert(request,page)
	size = request.session['size'] = get_image_size(request,page)
	c['image_width'] =size[0]
	c['image_height'] =size[1]
	c['status'] = 'success'
	c['img_url'] = '/'.join(path.split('/')[:-1]).split('/static/')[-1]+'/'+str(page)+'.png'
	c['total_page'] = request.session['total_page']
	c['username'] = request.session.get('username')
	c['page'] = page
	c['owner_guid'] = request.session['owner_guid']
	print('page: '+str(request.session['page']))
	return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def select_page(request):
	c={}
	path = request.session['path']
	page = int(request.POST.get('selected_page'))
	if not 1 <= page <= request.session.get('total_page'):
		c['status'] = 'fail'
	else:
		check_and_convert(request,page)
		size = request.session['size'] = get_image_size(request,page)
		c['image_width'] =size[0]
		c['image_height'] =size[1]
		c['status'] = 'success'
		c['page'] = page
		request.session['page'] = page
		c['total_page'] = request.session['total_page']
		c['username'] = request.session.get('username')
		c['owner_guid'] = request.session['owner_guid']
		print('page: '+str(request.session['page']))
	print(c)


	return JsonResponse(c)

def check_and_convert(request,p):
	path = request.session['path']
	page = int(p)
	check_path= '/'.join(path.split('/')[:-1])+'/'+str(page)+'.png'
	if not request.session.get('resolution'):
		request.session['resolution'] = '400'
	if not os.path.exists(check_path):
		print('not exists')
		img_path = '/'.join(path.split('/')[:-1]) +'/'+str(page)+'.png'
		cmd = 'python3 %s %s %s %s %s %s %s' %(BASE_DIR+'/user/static/scripts/convert_to_img.py',path, str(page), request.session['resolution'],'0',img_path,'1')
		print(cmd)
		os.system(cmd)
	while not os.path.exists(check_path):
		time.sleep(0.05)
	return 'mission complete'
	

def get_image_size(request,p):
	path = request.session['path']
	page = int(p)
	check_path= '/'.join(path.split('/')[:-1])+'/'+str(page)+'.png'
	img = Image.open(check_path)
	print(check_path.split('/')[-1] +' size ' +str(img.size[0]) +' , '+ str(img.size[1]))
	return img.size


# @csrf_exempt
# def add_box(request):
# 	page = request.session['page']
# 	file_guid = request.session['file_guid']

@csrf_exempt
# 将传回的string解析成 object 然后写入数据库
def save_change_to_server(request):
	# print(request.POST)
	canvas_height = request.POST.get('canvas_height')
	canvas_width = request.POST.get('canvas_width')
	original_height = request.POST.get('original_height')
	original_width =request.POST.get('original_width')
	added_backups = request.POST.get('added_backups','')
	returned_backups = request.POST.get('returned_backups','')
	deleted_backups = request.POST.get('deleted_backups','')

	# print('canvas_height: ' + canvas_height)
	# print('canvas_width: '+canvas_width)
	# print('original_height: '+original_height)
	# print('original_width: '+original_width)
	# print('added_backups: '+added_backups)
	# print('returned_backups: '+returned_backups)
	# print('deleted_backups: '+deleted_backups)
	# print(added_backups[1:][:-1].split('}'))
	added = to_json_object(added_backups)
	deleted = to_json_object(deleted_backups)
	returned = to_json_object(returned_backups)
	add_to_sql(request,added,original_width,original_height,canvas_width,canvas_height)
	# delete_from_sql(request,deleted)
	# to_sql(returned) # 没必要 
	# print('added: '+json.loads(added_backups[0]))
	# print(request.session['file_guid'])
	# print(request.session['username'])
	# print(request.session['path'])
	save_path = '/'.join(request.session['path'].split('/')[:-1])+'/'+request.session['username']+'/'
	txt_path =save_path+str(request.session['page'])+'.txt'
	print(save_path)
	return JsonResponse({'save_path':save_path})


# string转换成 JSON object的list
def to_json_object(string):
	ans = []
	for i in string[1:][:-1].split('},'):
		if i == None or i == '':
			continue
		ans.append(json.loads(i+'}')) if i[-1] != '}' else ans.append(json.loads(i))
	return ans

# class Object(models.Model):
# 	object_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)
# 	file = models.ForeignKey(File, on_delete=models.CASCADE)
# 	category = models.PositiveIntegerField() #figure
# 	coordinate = models.CharField(max_length=256,default='') # "shang,xia,zuo,you"
# 	status = models.CharField(max_length=256,default='')
# 	editor = models.ForeignKey(User, on_delete=models.CASCADE,default = None)
# 	page = models.PositiveIntegerField(default = 1)
#把object加入数据库
@csrf_exempt

def add_to_sql(request,added,ow,oh,cw,ch):
	print(request.session['file_guid'])
	print(request.session['username'])
	print(request.session['path'])
	print(added)

	this_user = User.objects.filter(username = request.session['username'])[0]
	this_file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	for i in added:
		# print(box_category)
		obj = Object()
		# 左右上下
		obj.left = int(i['coordinates'][0])
		obj.right = int(i['coordinates'][1])
		obj.top = int(i['coordinates'][2])
		obj.bot = int(i['coordinates'][3])
		obj.coordinate = str(i['coordinates'])
		obj.category = box_category[i['category']]
		obj.file = this_file
		obj.editor = this_user
		obj.page = int(request.session['page'])
		obj.save()
		# obj.status = 'added'
		# obj.save()
		# print('--------')
		# print(obj.coordinate)
		# print(obj.page)
		# print(obj.file.filename)
		# print(obj.editor.username)
		# print(obj.category)
		# print('++++++++')
		# 
		# print(request.session['page'])
		# print(this_file.filename)
		# print(this_user.username)
	return 'yes'

def get_boxes(request):
	ans = []
	this_user = User.objects.filter(username = request.session['username'])[0]
	this_file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	page = request.session['page']
	boxes =Object.objects.filter(editor = this_user).filter(file = this_file).filter(page=page)
	for i in boxes:
		print(i)

	return

def return_OCR_results(request):
	ans = []
	this_user = User.objects.filter(username = request.session['username'])[0]
	this_file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	page = request.session['page']
	boxes =Object.objects.filter(editor = this_user).filter(file = this_file).filter(page=page)
	for i in boxes:
		# 左右上下
		box = {'category':rev_box_category[i.category],'coordinates':[(i.left), (i.right), (i.top), (i.bot)]}
		# print(box)
		ans.append(box)
	return JsonResponse(ans,safe=False)


# 导出所有我的标注，生成txt文件，提供下载
@csrf_exempt
def get_my_data(request):
	this_user = User.objects.filter(username = request.session['username'])[0]
	this_file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	txt_path = '/'.join(this_file.path.split('/')[:-1])+'/my_txt_files/'
	zip_content_path = '/'.join(this_file.path.split('/')[:-1])
	# zip_path = '/'.join(this_file.path.split('/')[:-2])+this_file.filename+'_'+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	zip_path = this_file.filename+'_'+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	# 如果有某页的记录，则加入到zip_page
	zip_pages = set()
	total_page = this_file.total_page
	print(txt_path)
	print(zip_content_path)
	print(zip_path)
	# 文件夹是否存在
	if not os.path.exists(txt_path):
		os.makedirs(txt_path)
	for i in range(1,total_page+1):
		boxes =Object.objects.filter(editor = this_user).filter(file = this_file).filter(page = i)
		if boxes.count():
			write_into_txt(request,txt_path,boxes,i,request.session['username'])
			zip_pages.add(i)

	user_dir = '/'.join(this_file.path.split('/')[:-2]) # 用户的文件夹所在的目录，换到那个目录下去创建zipfile
	this_dir= os.getcwd() 								# 再换回来
	# 创建 zip文件
	zip(this_file.filename, zip_path+'.zip',zip_pages,this_dir,user_dir)
	# 被用户下载的文件的名称
	download_name = (this_file.filename +'_my_data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+'.zip'
	print(download_name)
	file=open(user_dir +'/'+zip_path+'.zip','rb')  
	# file=open(zip_path+'.tar.gz','rb') 
	response =StreamingHttpResponse(file)  
	response['Content-Type']='application/octet-stream' 
	response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(download_name))
	return response

# 导出整个组标记的data
@csrf_exempt
def get_group_data(request):
	this_user = User.objects.filter(username = request.session['username'])[0]
	this_file = File.objects.filter(file_guid = request.session['file_guid'])[0]
	txt_path = '/'.join(this_file.path.split('/')[:-1])+'/my_txt_files/'
	zip_content_path = '/'.join(this_file.path.split('/')[:-1])
	# zip_path = '/'.join(this_file.path.split('/')[:-2])+this_file.filename+'_'+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	zip_path = this_file.filename+'_'+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	# 如果有某页的记录，则加入到zip_page
	zip_pages = set()
	total_page = this_file.total_page
	print(txt_path)
	print(zip_content_path)
	print(zip_path)
	# 文件夹是否存在
	if not os.path.exists(txt_path):
		os.makedirs(txt_path)

	# 首先查询文件都分享给谁过。。。（别忘了owner自己）
	print(this_user.username)
	shares = Share.objects.filter(shared_file=this_file)
	for i in shares:
		this_editor = i.share_user
		print('editor_name: ' + this_editor.username)
		if this_editor == this_user:
		 # 如果登录的用户是被分享的,跳过此循环
			print('it is me')
			continue
		for j in range(1,total_page+1):
			boxes =Object.objects.filter(editor = this_editor).filter(file = this_file).filter(page = j)
			if boxes.count():
				write_into_txt(request,txt_path,boxes,j,this_editor.username)
				zip_pages.add(j)
	#自己的标注
	for i in range(1,total_page+1):
		boxes =Object.objects.filter(editor = this_user).filter(file = this_file).filter(page = i)
		if boxes.count():
			write_into_txt(request,txt_path,boxes,i,request.session['username'])
			zip_pages.add(i)

	# shutil.make_archive(zip_path, 'zip', zip_content_path)
	user_dir = '/'.join(this_file.path.split('/')[:-2]) # 用户的文件夹所在的目录，换到那个目录下去创建zipfile
	this_dir= os.getcwd() 								# 再换回来
	# 创建 zip文件
	zip(this_file.filename, zip_path+'.zip',zip_pages,this_dir,user_dir)
	# 被用户下载的文件的名称
	download_name = (this_file.filename +'_my_data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+'.zip'
	print(download_name)
	file=open(user_dir +'/'+zip_path+'.zip','rb')  
	# file=open(zip_path+'.tar.gz','rb') 
	response =StreamingHttpResponse(file)  
	response['Content-Type']='application/octet-stream' 
	response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(download_name))
	return response




# 将数据库条目写入txt文件， 格式为 左,右,上,下 \t category \r\n,boxes为对editor,file_guid, page 的queryset
def write_into_txt(request,path,boxes,page,editor_name):
	content = ''
	for box in boxes:
		content += str(box.left)+','+str(box.right)+','+str(box.top)+','+str(box.bot)+'\t'+rev_box_category[box.category]+'\r\n'
	print(page)
	print(content)
	f = open(path +str(page)+'-'+editor_name+'.txt','wb')
	f.write(content.encode())
	f.close()
	return

 
# 一次性打包整个根目录。空子目录会被打包。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
# output_filename:完整的文件名， source_dir: 源文件夹
def make_targz(output_filename, source_dir):
	with tarfile.open(output_filename, "w:gz") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))
	return 

# 用这个
# src 是要打包的文件夹, des 是输出文件'xxx.zip', arr是页码的array
# 如果某一页没有标注数据的话，就不用包括对应的图片了
def zip(src,des,arr,original_dir,new_dir):
	# 是否压缩
	try:
		import zlib
		compression = zipfile.ZIP_DEFLATED
	except:
		compression = zipfile.ZIP_STORED
	os.chdir(new_dir)
	print('change to dir: ' + os.getcwd())
	modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}
	print('creating archive')
	z = zipfile.ZipFile(des, 'w')
	for (root,dirs,files) in os.walk(src):
		for file in files:
			print(os.path.join(root, file))
			# z.write(os.path.join(root, file),compress_type=compression)
			filename, ext = os.path.splitext(file)
			if ext == '.png' and int(filename) in arr:
				# fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), src), mode)
				z.write(os.path.join(root, file).split('/static/')[-1],compress_type=compression)
			if ext == '.txt' and int(filename.split('-')[-2]) in arr:
				# fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), src), mode)
				z.write(os.path.join(root, file).split('/static/')[-1],compress_type=compression)	
	z.close()
	os.chdir(original_dir)
	print('back to dir: ' + os.getcwd())

# 改变 PDF转 iamge时候的resolution， 默认是400
@csrf_exempt
@ensure_csrf_cookie
def change_resolution(request):
	print('change_resolution')
	resolution = request.session['resolution'] = str(request.POST.get('resolution'))
	print(resolution)
	c = {}
	c['message'] = 'success: ' +resolution
	c['resolution'] = resolution
	return JsonResponse(c)

box_category={
	'formula':1,
	'table':2,
	'figure':3,
}

rev_box_category={
	1:'formula',
	2:'table',
	3:'figure',
}


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    ------------------------------------------------------------------------------------------------------------


#
# 用户群组
#
#创建群组
@ensure_csrf_cookie
@csrf_exempt
#@login_required(login_url='/user/login/')
def create_group(request):
	c = {}
	correct_members = []
	wrong_input = []

	if request.method == 'POST':
		if User.objects.filter(user_guid = request.session['user_guid']).count():
			owner = User.objects.filter(user_guid = request.session['user_guid'])[0]
		else:
			return JsonResponse({'message':'error, log in please'})
		id_input = request.POST.get('members').split('\n')
		name_input = request.POST.get('name')

		if Group.objects.filter(group_name=name_input).exists():   # check if group with same name exists
			c = {'error': 'duplicate', }
			return JsonResponse(c)
		else:
			group = Group(owner=owner, group_name=name_input)
			group.save()

		for p in id_input:
			if User.objects.filter(Q(username=p) | Q(email=p)).exists():
				matched_user = User.objects.filter(Q(username=p) | Q(email=p))[0]
				gm = GroupMember(share_group=group, shared_user=matched_user)
				gm.save()
				correct_members.append(p)
			else:
				wrong_input.append(p)

		# if no valid group member is found, delete the generated group
		if len(correct_members) == 0:
			group.delete()

		gm = GroupMember(share_group=group, shared_user=owner);
		gm.save()

	c['correct_members'] = correct_members
	c['wrong_input'] = wrong_input
	return JsonResponse(c)


#@login_required(login_url='/user/login/')
def group_management(request):
	if User.objects.filter(user_guid = request.session['user_guid']).count():
		user = User.objects.filter(user_guid = request.session['user_guid'])[0]
		# print(user) 
	groups = Group.objects.filter(owner=user)

	print(user)
	print(groups)

	# for group in groups:   # find the members in each group and store username in array (as string?)
	#     members = GroupMember.objects.filter(share_group=group)

	c = {
		'groups': groups,
		'user': user,
	}
	t = loader.get_template('group_management.html')
	return HttpResponse(t.render(c,request))
	# return render(request, 'group_management.html', context)
	# return HttpResponse('asd')

#@login_required(login_url='/user/login/')
def shared_group_management(request):
	user = None
	if User.objects.filter(user_guid = request.session['user_guid']).count():
		user = User.objects.filter(user_guid = request.session['user_guid'])[0]
		records = GroupMember.objects.select_related('share_group').filter(shared_user=user)  # includes groups user owned, handle in html
	context = {
		'records': records,
		'user': user,
	}
	return render(request, 'shared_group_management.html', context)


#@login_required(login_url='/user/login/')
def edit_group(request, group_guid):
	if User.objects.filter(user_guid = request.session['user_guid']).count():
		user = User.objects.filter(user_guid = request.session['user_guid'])[0]
	print(group_guid)
	thegroup = Group.objects.select_related().filter(group_guid=group_guid)[0]
	members = GroupMember.objects.filter(share_group=thegroup)

	context = {
		'group': thegroup,
		'members': members,
		'user': user,
	}
	for i in members:
		print(i.shared_user.username)
	return render(request, 'edit_group.html', context)

@ensure_csrf_cookie
@csrf_exempt
#@login_required(login_url='/user/login/')
def delete_member(request):
	group_guid = request.POST.get('group')
	thegroup = Group.objects.select_related().filter(group_guid=group_guid)[0]
	print(thegroup)
	user = None
	if User.objects.filter(user_guid = request.session['user_guid']).count():
		user = User.objects.filter(user_guid = request.session['user_guid'])[0]

	c = {}
	correct_members = []
	wrong_input = []
	if request.method == 'POST':
		to_delete = request.POST.getlist('to_delete[]')
		# to_delete = request.POST['to_delete']
		print(to_delete)
		for p in to_delete:
			if User.objects.filter(username=p).exists(): # if matched_user is valid, do the deletion
				matched_user = User.objects.filter(username=p)[0]
				if matched_user == user:
					c['message'] = '无法删除群主'
					return JsonResponse(c)
				else:
					GroupMember.objects.filter(share_group=thegroup, shared_user=matched_user).delete()
					correct_members.append(p)
			else:
				wrong_input.append(p)

	c['correct_members'] = correct_members
	c['wrong_input'] = wrong_input
	return JsonResponse(c)


@ensure_csrf_cookie
@csrf_exempt
def add_member(request):
    c = {}
    correct_members = []
    wrong_input = []

    if request.method == 'POST':
        group_guid = request.POST.get('group')
        group = Group.objects.filter(group_guid=group_guid)[0]
        id_input = request.POST.get('members').split('\n')

        for p in id_input:
            if User.objects.filter(username= p).count():
                matched_user = User.objects.filter(username = p)[0]
                gm = GroupMember(share_group=group, shared_user=matched_user)
                gm.save()
                correct_members.append(p)
                print(gm)
                print(GroupMember.objects.count())
            else:
                wrong_input.append(p)
    print('--------------------')
    for i in GroupMember.objects.all():
    	print(i)
    c['correct_members'] = correct_members
    c['wrong_input'] = wrong_input
    return JsonResponse(c)



# @ensure_csrf_cookie
# @csrf_exempt
# def add_member(request):
# 	c = {}
# 	correct_members = []
# 	wrong_input = []
# 	group=None
# 	user = None
# 	# print(request.POST['group'])
# 	# print(request.POST['members'])
# 	# c = 0
# 	# if Group.objects.filter(group_guid = request.POST['group']).count():
# 	# 	group = Group.objects.filter(group_guid = request.POST['group'])[0]
# 	# 	print('group_name: ' + group.group_name)
# 	# for i in request.POST['members'].split('\n'):
# 	# 	if User.objects.filter(username = i).count():
# 	# 		user = User.objects.filter(username = i)[0]
# 	# 		print('user: ' + user.username)
# 	# 		gm=GroupMember()
# 	# 		gm.shared_user = user
# 	# 		gm.share_group = group
# 	# 		gm.save()
# 	# 		c +=1
# 	# 		print(c)
# 	# 		print(gm)
# 	# return JsonResponse({'a':'b'})




# 	if request.method == 'POST':
# 		if User.objects.filter(user_guid = request.session['user_guid']).count():
# 			user = User.objects.filter(user_guid = request.session['user_guid'])[0]
# 		group_guid = request.POST.get('group')
# 		group = Group.objects.select_related().filter(group_guid=group_guid)[0]
# 		id_input = request.POST.get('members').split('\n')

# 		for p in id_input:
# 			# print(p)
# 			if User.objects.filter(Q(username=p) | Q(email=p)).exists():
# 				matched_user = User.objects.filter(Q(username=p) | Q(email=p))[0]
# 				print(matched_user.username)
# 				gm = GroupMember()
# 				gm.share_group=group
# 				gm.shared_user=matched_user
# 				gm.save()
# 				correct_members.append(p)
# 			else:
# 				wrong_input.append(p)

# 	c['correct_members'] = correct_members
# 	c['wrong_input'] = wrong_input
# 	print('aaaaaa')
# 	for i in GroupMember.objects.filter(share_group=group):
# 		print(i.shared_user.username)
# 	return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def delete_group(request):
	c = {}
	user = None
	if request.method == 'POST':
		if request.POST.get('group') != None:
			if User.objects.filter(user_guid = request.session['user_guid']).count():
				user = User.objects.filter(user_guid = request.session['user_guid'])[0]
			target_group_guid = request.POST.get('group')
			target_group = Group.objects.filter(group_guid=target_group_guid)[0]
			if target_group.owner != user:
				c['message'] = '非群创建者，没有操作权限'
				return JsonResponse(c)
			else:
				# Delete related record from GroupMember table by CASCADE
				Group.objects.filter(group_guid=target_group_guid).delete()
				c['message'] = '删除成功'
				return JsonResponse(c)
	# else:
	#     return render(request, '')


#  -----------------------------------------------------------------------------------------------------------------


#
# 文件管理系统
#
#@login_required(login_url='/user/login/')
def index(request):
	# return redirect('/user/file_upload')
	return redirect(reverse('user:file_upload'))


#@login_required(login_url='/user/login/')
def homepage(request):
	return render(request, 'user/user_homepage.html')


# #@login_required(login_url='/user/login/')
# def file_upload(request):
# 	form = FileUploadForm(request.POST or None, request.FILES or None)
# 	if form.is_valid():
# 		file = form.save(commit=False)
# 		file.owner = request.user
# 		file.path = request.FILES['path']
# 		file.filename = request.FILES['path'].name

# 		if File.objects.filter(filename=file.filename).filter(owner=file.owner):
# 			context = {
# 				'file': file,
# 				'form': form,
# 				'error_message': '同名文件已存在',
# 				'show': 1,
# 			}
# 			return render(request, 'file/upload.html', context)
# 		else:
# 			# 检查文件后缀名
# 			file_type = file.path.url.split('.')[-1]
# 			file_type.lower()
# 			if file_type not in UPLOAD_FILE_TYPES:
# 				context = {
# 					'file': file,
# 					'form': form,
# 					'show': 2,
# 				}
# 				return render(request, 'file/upload.html', context)
# 			file.save()
# 			context = {
# 				'form': form,
# 				'show': 0,
# 			}
# 			return render(request, 'file/upload.html', context)
# 	context = {
# 		'form': form,
# 		# 'show': 2,  # do nothing - no alert
# 	}
# 	return render(request, 'file/upload.html', context)

# @csrf_exempt
# def file_upload(request):
#     c = {}
#     if request.method == 'POST':
#         obj = request.FILES.get('file')
#         filename = obj.name
#         owner = request.user
#
#         if File.objects.filter(filename=filename).filter(owner=owner).count():
#             c['message'] = '已存在同名文件'
#             return JsonResponse(c)


#@login_required(login_url='/user/login/')
# def file_management(request):
# 	user = request.user
# 	files = File.objects.filter(owner=user)
# 	if files.exists():
# 		msg_code = 0
# 	else:
# 		msg_code = 1
# 	context = {
# 		'user': user,
# 		'files': files,
# 		'msg': msg_code,
# 	}
# 	return render(request, 'file/file_management.html', context)


#@login_required(login_url='/user/login/')
def share_file_view(request):
	user = None
	if User.objects.filter(user_guid = request.session['user_guid']).count():
		user = User.objects.filter(user_guid = request.session['user_guid'])[0]
	shared_files = FileShare.objects.filter(sharer=user)
	if shared_files.exists():
		msg_code = 0
	else:
		msg_code = 1
	context = {
		'user': user,
		'shared_files': shared_files,
		'msg': msg_code,
	}
	return render(request, 'file/shared_with_me.html', context)

#@login_required(login_url='/user/login/')
def group_file_view(request):   # TODO: complete function
	return render(request, 'check_success.html')


# @ensure_csrf_cookie
# @csrf_exempt
# #@login_required(login_url='/user/login/')
# def delete_file(request):
# 	c = {}
# 	if request.method == 'POST':
# 		if request.POST.get('file_guid') != None:
# 			user = request.user
# 			target_file_id = request.POST.get('file_guid')
# 			target_file = File.objects.filter(gu_id=target_file_id)[0]
# 			if target_file.owner != user:
# 				c['message'] = '非文件上传者，无法删除'
# 				return JsonResponse(c)
# 			else:
# 				# delete from File table, other table auto-delete by CASCADE
# 				File.objects.filter(gu_id=target_file_id).delete()
# 				c['message'] = '删除成功'  # TODO: delete from file storage
# 	return JsonResponse(c)


# @ensure_csrf_cookie
# @csrf_exempt
# #@login_required(login_url='/user/login/')
# def share_file(request):
# 	c = {}
# 	correct_co_editors = []
# 	wrong_input = []

# 	if request.method == 'POST':
# 		owner = request.user
# 		file_guid = request.POST.get('file_guid')
# 		share_input = request.POST.get('co_editors').split('\n')

# 		shared_file = File.objects.filter(gu_id=file_guid)[0]
# 		for p in share_input:
# 			if User.objects.filter(Q(username=p) | Q(email=p)).exists():  # input has a match
# 				matched_editor = User.objects.filter(Q(username=p) | Q(email=p))[0]
# 				correct_co_editors.append(p)
# 				share = FileShare(owner=owner, sharer=matched_editor, shared_file=shared_file)
# 				share.save()
# 				prin
# 			else:
# 				wrong_input.append(p)

# 	c['correct_co_editors'] = correct_co_editors
# 	c['wrong_input'] = wrong_input
# 	return JsonResponse(c)


@ensure_csrf_cookie
@csrf_exempt
#@login_required(login_url='/user/login/')
def share_file_to_group(request):
	c = {}
	correct_group = []
	wrong_input = []
	user = None
	if request.method == 'POST':
		if User.objects.filter(user_guid = request.session['user_guid']).count():
			user = User.objects.filter(user_guid = request.session['user_guid'])[0]
		file_guid = request.POST.get('file_guid')
		share_input = request.POST.get('co_groupID').split('\n')

		shared_file = File.objects.filter(gu_id=file_guid)[0]
		for p in share_input:
			if Group.objects.filter(group_guid=p).exists():   # found match
				matched_group = Group.objects.select_related().filter(group_guid=p)[0]
	return render(request, 'check_success.html')


# edit_fileedit_file
#@login_required(login_url='/user/login/')
# def edit_file(request):  # TODO: complete function
# 	return render(request, 'check_success.html')
