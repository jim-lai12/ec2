# -*- coding: utf-8 -*-

import boto3
import threading
import Queue
import time
import random
import paramiko
import time
from sshconnection import SSHConnection






class EC2(object):
	def __init__(self, keyfile,keyname,instance,securitygroup):
		self.keyfile = keyfile
		self.keyname = keyname
		self.instance = instance
		self.securitygroup = securitygroup
		self.numbernow = 0
		self.nametable = {}
		self.workstatus = False
		self.msg = Queue.Queue()
		#self.command = Queue.Queue()
		self.needcommand = Queue.Queue()
		self.opencommand = Queue.Queue()
		self.uploadcommand = Queue.Queue()
		self.downloadcommand = Queue.Queue()
		self.execommand = Queue.Queue()


	def openserver(self):
		self.workstatus = True
		self.needcommand.put(["open","要開幾台伺服器?"])
		inputnum = int(self.opencommand.get())
		ec2 = boto3.resource('ec2')
		instances = ec2.instances.filter()
		dict = {}
		num = 0
		for instance in instances:
			if instance.state["Name"] != "terminated":
				num = num + 1
			if instance.tags:
				for tags in instance.tags:
					if tags["Key"] == 'Name':
						dict[instance.id] = tags["Value"]
		if num >= inputnum:
			self.msg.put( "伺服器數量足夠" )
			ordered = change(dict)
		else:
			self.msg.put( "需要開" + str(inputnum - num) + "台伺服器" )
			self.needcommand.put(["open","input ami id:"])
			ami = self.opencommand.get()
			self.create((inputnum - num), (num + 1), ami)
			for instance in instances:
				if instance.state["Name"] != "terminated":
					num = num + 1
				if instance.tags:
					for tags in instance.tags:
						if tags["Key"] == 'Name':
							dict[instance.id] = tags["Value"]
			ordered = change(dict)
		self.msg.put("等待開啟伺服器...")
		i = 1
		while i <= inputnum:
			ec2.Instance(ordered[str(i)]).start()
			i = i + 1
		i = 1
		while i <= inputnum:
			ec2.Instance(ordered[str(i)]).wait_until_running()
			i = i + 1
		self.msg.put( "檢查伺服器中..." )
		k = False
		while k == False:
			for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
				if status[u'InstanceStatus'][u'Status'] == "ok":
					k = True
				else:
					k = False
			time.sleep(10)
		self.msg.put( "所有伺服器皆可使用!!!" )
		self.nametable = ordered
		self.numbernow = inputnum
		self.workstatus = False

	def close(self):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		i = 1
		while i <= self.numbernow:
			ec2.Instance(self.nametable[str(i)]).stop()
			i = i + 1
		self.nametable = {}
		self.numbernow = 0
		self.workstatus = False

	def commandexe(self,uselist):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		self.needcommand.put(["exe","需要執行的命令(執行python檔案需要加/usr/bin/python2.7): "])
		command = self.execommand.get()
		x = []
		for i in uselist:
			ip = ec2.Instance(self.nametable[i]).public_dns_name
			x.append(threading.Thread(target=self.exe, args = (ip, command,)))
			x[len(x)-1].start()
		# exe(ip,command)
		self.workstatus = False

	def exe(self,ip, command):
		ssh = SSHConnection(ip,self.keyfile)
		ssh.connect()
		nomal, exception = ssh.cmd(command)
		if exception == "":
			self.msg.put(nomal)
		else:
			self.msg.put( exception )
		ssh.close()

	def create(self,num, name, ami):
		ec2 = boto3.resource('ec2')
		instances = ec2.create_instances(
			ImageId=ami,
			InstanceType=self.instance,
			KeyName=self.keyname,
			MinCount=num,
			MaxCount=num,
			SecurityGroupIds=[self.securitygroup],
		)
		for item in instances:
			dic = {'Key': 'Name', 'Value': str(name)}
			ec2.create_tags(Resources=[item.id], Tags=[dic])
			name = name + 1

	def download(self,uselist):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		self.needcommand.put(["download","在這裡原始檔名:  "])
		local = self.downloadcommand.get()
		self.needcommand.put(["download","下載後檔名(可加路徑,副檔名另加):  "])
		new = self.downloadcommand.get()
		self.needcommand.put(["download","副檔名(不用加點):  "])
		mode = self.downloadcommand.get()
		x = []
		for i in uselist:
			x.append(threading.Thread(target=self.downloadfun, args = (ec2,i,local,new,mode,)))
			x[len(x)-1].start()
		self.workstatus = False


	def upload(self,uselist):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		self.needcommand.put(["upload","在這裡原始檔名:  "])
		local = self.uploadcommand.get()
		self.needcommand.put(["upload","上傳後新檔名:  "])
		new = self.uploadcommand.get()
		x = []
		for i in uselist:
			x.append(threading.Thread(target=self.uploadfun, args = (ec2,i,local,new,)))
			x[len(x)-1].start()
		self.workstatus = False

	def uploadbysort(self,uselist):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		self.needcommand.put(["upload","在這裡原始檔名(可加路徑,副檔名另加):  "])
		localname = self.uploadcommand.get()
		self.needcommand.put(["upload","副檔名(不用加點):  "])
		localextension = self.uploadcommand.get()
		self.needcommand.put(["upload","上傳後新檔名:  "])
		new = self.uploadcommand.get()
		x = []
		for i in uselist:
			local = localname+str(i)+"."+localextension
			x.append(threading.Thread(target=self.uploadfun, args = (ec2,i,local,new,)))
			x[len(x)-1].start()
		self.workstatus = False



	def downloadfun(self,ec2, i, local, new, mode):
		ip = ec2.Instance(self.nametable[str(i)]).public_dns_name
		ssh = SSHConnection(ip,self.keyfile)
		ssh.connect()
		ssh.download(local, new + str(i) + "." + mode)
		ssh.close()

	def uploadfun(self,ec2, i, local, new):
		ip = ec2.Instance(self.nametable[str(i)]).public_dns_name
		ssh = SSHConnection(ip,self.keyfile)
		ssh.connect()
		ssh.upload(local, new)
		ssh.close()


def change(d):
	d2 = {}
	for item in d:
		d2[d[item]] = item
	return d2
















































































































