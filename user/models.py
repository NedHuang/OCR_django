from django.db import models
import django.utils.timezone as timezone
# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=256)		#用户名
	user_guid = models.CharField(max_length=256)	#用户GUID
	password = models.CharField(max_length=256)		#用户密码
	cellphone = models.CharField(max_length=256)	#用户电话号码
	email = models.CharField(max_length=256)		#用户的邮箱
	account_type = models.CharField(max_length=256)	#账户类型
	groups = models.TextField(default ='')						#用户所属的组
	co_edit_files = models.TextField(default='')				#用户可以编辑的文件（共享但不拥有）

	date_registration = models.DateTimeField('date account created', default=timezone.now)
	date_last_login = models.DateTimeField('date last logined', auto_now = True)

	def instr(self):
		return 'username: '+self.username+'\tuser_guid: '+self.user_guid+'\tpassword: '\
		+self.password+'\tcellphone: '+self.cellphone+'\temail: '+self.email+'account_type: '\
		+self.account_type+'date_registration: '+str(self.date_registration)+'date_last_login: '\
		+str(self.date_last_login)


class File(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)	#文件的所有者（上传）
	file_guid = models.CharField(max_length=256)				#文件的GUID
	co_editor = models.TextField(default ='')					#可以标注的人
	groups = models.TextField(default ='')						#可以标注的组
	filename = models.CharField(max_length=256)					#文件原名
	path = models.CharField(max_length=256)						#文件存储路径

	date_uploaded = models.DateTimeField('date file uploaded', default=timezone.now)
	last_modified = models.DateTimeField('date last modified', auto_now = True)



	def instr(self):
		return 'owner: '+self.owner.username+'\tfilename: '+self.filename+'\tfile_guid: ' \
		+self.file_guid+'\tpath: '+ self.path+'\tdate_upload: '+str(self.date_uploaded)\
		+'\tlast_modified' + str(self.last_modified)

class Object(models.Model):
	file_id = models.ForeignKey(File, on_delete=models.CASCADE)
	category = models.CharField(max_length=256,default='') #figure
	coordinate = models.CharField(max_length=256,default='') # "shang,xia,zuo,you"
	status = models.CharField(max_length=256,default='')
	# editor = models.CharField(max_length=256,default='')
	editor = models.ForeignKey(User, on_delete=models.CASCADE,default = None)


#operator:谁发起的共享, user_guid：分享给谁, permission
class Share(models.Model):
	file_guid = models.CharField(max_length=256,default='')
	user_guid = models.CharField(max_length=256,default='') 
	permission = models.CharField(max_length=256,default='')
	operator_guid = models.CharField(max_length=256,default='')


# the information about the group
class Group(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	group_id = models.CharField(max_length=256,default='')
	date_registration = models.DateTimeField('date account created', default=timezone.now)






# relationship between user and group 
class UserGroup(models.Model):
	user_guid = models.CharField(max_length=256,default='')
	group_id = models.CharField(max_length=256,default='')



#join groupuser and file_share
# group 单独的表
# 分享 -》单独的表
#权限:
#user_guid 是主键



