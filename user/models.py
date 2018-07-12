from django.db import models
import django.utils.timezone as timezone
# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=256)
	user_guid = models.CharField(max_length=256)
	password = models.CharField(max_length=256)
	cellphone = models.CharField(max_length=256)
	email = models.CharField(max_length=256)
	account_type = models.CharField(max_length=256)
	date_registration = models.DateTimeField('date account created', default=timezone.now)
	date_last_login = models.DateTimeField('date last logined', auto_now = True)

	def instr(self):
		return 'username: '+self.username+'\tuser_guid: '+self.user_guid+'\tpassword: '+self.password+'\tcellphone: '+self.cellphone+'\temail: '+self.email+'account_type: '+self.account_type


class File(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	fule_guid = models.CharField(max_length=256)
	filename = models.CharField(max_length=256)
	path = models.CharField(max_length=256)
	date_uploaded = models.DateTimeField('date file uploaded', default=timezone.now)
	pub_last_modified = models.DateTimeField('date last modified', auto_now = True)

