# -*- coding: utf-8 -*-

import boto3
import threading
import urllib
import Queue
import time
import random
import paramiko
import time
import gevent
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
		self.command = Queue.Queue()

	def openserver(self):
		self.workstatus = True
		self.msg.put("要開幾台伺服器?")
		inputnum = int(self.command.get())
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
			self.msg.put("input ami id:")
			ami = self.command.get()
			self.creat((inputnum - num), (num + 1), ami)
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

	def commandexe(self):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		use = []
		i = 1
		while i <= self.numbernow:
			use.append(str(i))
			i += 1
		self.msg.put("帳號需要除外?(y/n)")
		ex = self.command.get()
		notuse = []
		while ex == "y":
			self.msg.put("輸入想除外帳號序號(不需要了請按n,需要小於%d):  " % n)
			inputn = self.command.get()
			if inputn == "n":
				ex = "n"
			else:
				notuse.append(inputn)
		for item in notuse:
			use.remove(item)
		self.msg.put("需要執行的命令(執行python檔案需要加/usr/bin/python2.7):")
		command = self.command.get()
		x = []
		for item in use:
			ip = ec2.Instance(self.nametable[item]).public_dns_name
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

	def creat(self,num, name, ami):
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

	def download(self):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		i = 1
		self.msg.put("在這裡原始檔名:  ")
		local = self.command.get()
		self.msg.put("下載後檔名(可加路徑,副檔名另加):  ")
		new = self.command.get()
		self.msg.put("副檔名(不用加點):  ")
		mode = self.command.get()
		x = []
		while i <= self.numbernow:
			x.append(threading.Thread(target=self.downloadfun, args = (ec2,i,local,new,mode,)))
			x[len(x)-1].start()
			i = i + 1
		self.workstatus = False


	def upload(self):
		self.workstatus = True
		ec2 = boto3.resource('ec2')
		i = 1
		self.msg.put("在這裡原始檔名:  ")
		local = self.command.get()
		self.msg.put("上傳後新檔名:  ")
		new = self.command.get()
		x = []
		while i <= self.numbernow:
			x.append(threading.Thread(target=self.uploadfun, args = (ec2,i,local,new,)))
			x[len(x)-1].start()
			i = i + 1
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






























def ndownload(d,n):
	ec2 = boto3.resource('ec2')
	i = 1
	while i <= n:
		ip = ec2.Instance(d[str(i)]).public_dns_name
		ssh = SSHConnection(ip)
		ssh.connect()
		ssh.download("cookie.txt","cookie/cookie"+str(i)+".txt")
		ssh.download("userAgent.txt","userAgent/userAgent"+str(i)+".txt")
		ssh.download("logger.log","log/log"+str(i)+".log")
		#ssh.download("pay.txt", "pay/pay" + str(i) + ".txt")
		ssh.close()
		i = i + 1

def normalupload(d,n):
	ec2 = boto3.resource('ec2')
	i = 1
	while i <= n:
		ip = ec2.Instance(d[str(i)]).public_dns_name
		ssh = SSHConnection(ip)
		ssh.connect()
		ssh.upload("cookie/cookie"+str(i)+".txt","cookie.txt")
		ssh.upload("userAgent/userAgent"+str(i)+".txt","userAgent.txt")
		ssh.upload("config/config"+str(i)+".txt","config.txt")
		ssh.close()
		i = i + 1



def checklogin(d,n):
	ec2 = boto3.resource('ec2')
	x=[]
	i=1
	print "十分鐘內登入請稍後..."
	while i <=n :
		ip = ec2.Instance(d[str(i)]).public_dns_name
		x.append(gevent.spawn(checkloginexe, ip, str(i)))
		i=i+1
	gevent.joinall(x)
	i=1
	dic={}
	while i <=n :
		dic = dict(dic, **q.get())
		i=i+1
	f=open("logincheck.txt","w+")
	f.write(str(dic).replace(",","\n").replace("{","\n").replace("}","\n").replace(" ",""))
	f.close()

def checkloginexe(ip,i):
	d={}
	sleep = random.randint(0,300)
	print sleep
	time.sleep(sleep*60)
	ssh = SSHConnection(ip)
	ssh.connect()
	nomal, exception = ssh.cmd("/usr/bin/python2.7 logincheck.py")
	if exception == "":
		d[str(i)] = nomal
	else:
		d[str(i)] = exception
	ssh.close()
	q.put(d)




def main():
	task="0"
	while task!="exit":
		task = raw_input("1-全自動操作(開伺服器,上傳設定檔,檢查登入)\n2-開伺服器\n3-上傳特定檔案\n4-下載特定檔案\n5-確認登入\n6-執行\n7-下載Log檔,cookie\n8-關閉所有伺服器:\nexit-離開\n")
		if task == "1":
			d,n=openserver()
			normalupload(d,n)
		elif task == "2":
			d,n=openserver()
		elif task == "3":
			try:
				d,n
			except BaseException:
				print "先開伺服器"
			else:
				upload(d, n)
		elif task == "4":
			try:
				d,n
			except BaseException:
				print "先開伺服器"
			else:
				download(d, n)
		elif task == "5":
			try:
				d, n
			except BaseException:
				print "先開伺服器"
			else:
				checklogin(d,n)
		elif task == "6":
			try:
				d, n
			except BaseException:
				print "先開伺服器"
			else:
				commandexe(d, n)
		elif task == "7":
			try:
				d,n
			except BaseException:
				print "先開伺服器"
			else:
				ndownload(d,n)
		elif task == "8":
			try:
				d,n
			except BaseException:
				print "先開伺服器"
			else:
				close(d,n)
				del d,n
		elif task == "exit":
			print task
		else:
			print "重新選擇"
		print "\n\n\n\n\n\n\n"




#q=Queue.Queue()
#main()














































































































