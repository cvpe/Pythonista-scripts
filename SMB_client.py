# -*- coding: utf-8 -*-
# based   on   https://github.com/humberry/smb-example/blob/master/smb-test.py
# smb+nmb from https://github.com/miketeo/pysmb/tree/master/python3
# pyasn1  from https://github.com/etingof/pyasn1
from io import BytesIO
from smb.SMBConnection import SMBConnection
from smb import smb_structs
from nmb.NetBIOS import NetBIOS
import os
import sys
from socket import gethostname
from io import StringIO

class SMB_client():
	def __init__(self,username=None,password=None,smb_name=None):
		self.username     = username
		self.password     = password
		self.smb_name     = smb_name
		self.smb_ip       = None
		self.conn         = None
		self.service_name = None
		self.my_name      = None
		self.tree         = []

	def getBIOSName(self, remote_smb_ip, timeout=5):			# unused if dynamic IP
		# ip -> smb name
		try:
			bios = NetBIOS()
			srv_name = bios.queryIPForName(remote_smb_ip, timeout=timeout)
			return srv_name[0]
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			return None
			
	def getIP(self):
		# smb name -> ip
		try:
			bios = NetBIOS()
			ip = bios.queryName(self.smb_name)
			return ip[0]
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			return None
			
	def connect(self):
		try:
			self.my_name = gethostname()				# iDevice name
			self.smb_ip = self.getIP()
			smb_structs.SUPPORT_SMB2 = True
			self.conn = SMBConnection(self.username, self.password, self.my_name, self.smb_name, use_ntlm_v2 = True)
			self.conn.connect(self.smb_ip, 139)		#139=NetBIOS / 445=TCP
			if self.conn:
				shares = self.conn.listShares()
				for share in shares:
					if share.type == 0:		# 0 = DISK_TREE
						self.service_name = share.name  
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			
	def close(self):
		try:
			self.conn.close()
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)			
 
	def getRemoteDir(self, path, pattern):
		try:
			files = self.conn.listPath(self.service_name, path, pattern=pattern)
			return files
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			return None
				
	def getRemoteTree(self,path=''):
		try:
			if path == '':
				w = ''
			else:
				w = path+'/'
			files = self.getRemoteDir(path, '*')
			if files:
				for file in files:
					if file.filename[0] == '.':
						continue
					self.tree.append({'name':w+file.filename, 'isdir':file.isDirectory, 'size':file.file_size})
					if file.isDirectory:
						self.getRemoteTree(path=w+file.filename)
			return self.tree
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			return None

	def download(self, path, filename,buffersize=None,callback=None, local_path=None):
		try:
			#print('Download = ' + path + filename)
			attr = self.conn.getAttributes(self.service_name, path+filename)
			#print('Size = %.1f kB' % (attr.file_size / 1024.0))
			#print('start download')
			file_obj = BytesIO()
			if local_path:
				fw = open(local_path+filename, 'wb')
			else:
				fw = open(filename, 'wb')
			offset = 0
			transmit =0
			while True:
				if not buffersize:
					file_attributes, filesize = self.conn.retrieveFile(self.service_name, path+filename, file_obj)
				else:
					file_attributes, filesize = self.conn.retrieveFileFromOffset(self.service_name, path+filename, file_obj,offset=offset,max_length=buffersize)
					if callback:
						transmit = transmit + filesize
						callback(transmit)
				file_obj.seek(offset)
				for line in file_obj:
					fw.write(line)
				offset = offset + filesize
				if (not buffersize) or (filesize == 0):
					break
			fw.close()
			#print('download finished')
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			
	def upload(self, path, filename,buffersize=None,callback=None, local_path=None):
		try:
			#print('Upload = ' + path + filename)
			#print('Size = %.1f kB' % (os.path.getsize(filename) / 1024.0))
			#print('start upload')
			if local_path:
				file_obj = open(local_path+filename, 'rb')
			else:
				file_obj = open(filename, 'rb')
			offset = 0
			while True:
				if not buffersize:
					filesize = self.conn.storeFile(self.service_name, path+filename, file_obj)
					break
				else:	
					buffer_obj = file_obj.read(buffersize)			
					if buffer_obj:
						buffer_fileobj = BytesIO()
						buffer_fileobj.write(buffer_obj)
						buffer_fileobj.seek(0)
						offset_new = self.conn.storeFileFromOffset(self.service_name, path+filename, buffer_fileobj, offset=offset, truncate=False)
						#return the file position where the next byte will be written.
						offset = offset_new
						if callback:
							callback(offset)
					else:
						break
			file_obj.close()
			#print('upload finished')
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

	def delete_remote_file(self,path, filename):
		try:
			self.conn.deleteFiles(self.service_name, path+filename)
			#print('Remotefile ' + path + filename + ' deleted')
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

	def createRemoteDir(self, path):
		try:
			self.conn.createDirectory(self.service_name, path)
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
  
	def removeRemoteDir(self,path):
		try:
			self.conn.deleteDirectory(self.service_name, path)
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

	def renameRemoteFileOrDir(self,old_path, new_path):
		try:
			self.conn.rename(self.service_name, old_path, new_path)
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
