from django.db import models
import django.utils.timezone as timezone
import uuid
# Create your models here.

class User(models.Model):
	user_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)	#用户GUID
	username = models.CharField(max_length=256)		#用户名
	password = models.CharField(max_length=256)		#用户密码
	cellphone = models.CharField(max_length=256)	#用户电话号码
	email = models.CharField(max_length=256)		#用户的邮箱
	account_type = models.CharField(max_length=256)	#账户类型
	date_registration = models.DateTimeField('date account created', default=timezone.now)
	date_last_login = models.DateTimeField('date last logined', auto_now = True)

	def instr(self):
		return 'username: '+self.username+'\tuser_guid: '+str(self.user_guid)+'\tpassword: '\
		+self.password+'\tcellphone: '+self.cellphone+'\temail: '+self.email+'account_type: '\
		+self.account_type+'date_registration: '+str(self.date_registration)+'date_last_login: '\
		+str(self.date_last_login)


class File(models.Model):
	file_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)		#文件的GUID
	owner = models.ForeignKey(User, on_delete=models.CASCADE)	#文件的所有者（上传）
	filename = models.CharField(max_length=256)					#文件原名
	path = models.CharField(max_length=256)						#文件存储路径
	total_page = models.PositiveIntegerField(default=1)
	date_uploaded = models.DateTimeField('date file uploaded', default=timezone.now)
	last_modified = models.DateTimeField('date last modified', auto_now = True)



	def instr(self):
		return 'owner: '+self.owner.username+'\tfilename: '+self.filename+'\tfile_guid: ' \
		+self.file_guid+'\tpath: '+ self.path+'\tdate_upload: '+str(self.date_uploaded)\
		+'\tlast_modified' + str(self.last_modified)

class Object(models.Model):
	object_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)
	file = models.ForeignKey(File, on_delete=models.CASCADE)
	category = models.PositiveIntegerField() #figure
	coordinate = models.CharField(max_length=256,default='') # "shang,xia,zuo,you"
	status = models.CharField(max_length=256,default='')
	editor = models.ForeignKey(User, on_delete=models.CASCADE,default = None)
	page = models.PositiveIntegerField(default = 1)


#operator:谁发起的共享, user_guid：分享给谁, permission
class Share(models.Model):
	share_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)#文件的GUID
	shared_file = models.ForeignKey(File, on_delete=models.CASCADE, default = None)
	share_user = models.ForeignKey(User, on_delete=models.CASCADE, default = None,related_name='share_user')
	permission = models.CharField(max_length=256,default='')
	owner = models.ForeignKey(User, on_delete=models.CASCADE,default = None,related_name='share_owner')


# the information about the group
class Group(models.Model):
	group_guid = models.UUIDField(default=uuid.uuid4,null=False,auto_created=True,editable=False, primary_key=True)#文件的GUID
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	date_create = models.DateTimeField('date account created', default=timezone.now)


class FileGroup(models.Model):
	group = models.ForeignKey(Group,on_delete=models.CASCADE,default=None, primary_key=True)
	File = models.ForeignKey(File,on_delete=models.CASCADE,default=None)



# relationship between user and group 
class UserGroup(models.Model):
	group = models.ForeignKey(Group,on_delete=models.CASCADE,default=None, primary_key=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE,default=None)




#join groupuser and file_share
# group 单独的表
# 分享 -》单独的表
#权限:
#user_guid 是主键



