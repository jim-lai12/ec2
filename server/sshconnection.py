# -*- coding: utf-8 -*-


import paramiko


class SSHConnection(object):
	def __init__(self, host,key_filename, port=22, username='ubuntu', pwd=''):
		self.host = host
		self.port = port
		self.username = username
		self.pwd = pwd
		self.key_filename=key_filename

	def connect(self):
		private_key = paramiko.RSAKey.from_private_key_file(self.key_filename)
		transport = paramiko.Transport((self.host, self.port))
		transport.connect(username=self.username, password=self.pwd,pkey=private_key)
		self.__transport = transport

	def close(self):
		self.__transport.close()

	def cmd(self, command):
		ssh = paramiko.SSHClient()
		ssh._transport = self.__transport
		stdin, stdout, stderr = ssh.exec_command(command)
		return stdout.read(),stderr.read()

	def upload(self, local_path, target_path):
		sftp = paramiko.SFTPClient.from_transport(self.__transport)
		sftp.put(local_path, target_path)

	def download(self, local_path, target_path):
		sftp = paramiko.SFTPClient.from_transport(self.__transport)
		sftp.get(local_path, target_path)













































































































