import requests
import json
import os
import time
import SystemManager
import MessageManager

CONFIG_PATH = 'json/config'
LOCK_API_ROOT = 'https://api.lockitron.com/v2'

class LockManager:
	def __init__(self):
		self.systemManager = SystemManager.SystemManager()
		self.messageManager = MessageManager.MessageManager()

	def doUnlock(self, user):
		# Do unlock
		if not self.unlock():
			return False
		#then log & send message to host
		self.messageManager.sendMessage("Welcome home, " + user, self.messageManager.getHostPhone())
		self.systemManager.writeSystemLog('User ' + user + ' unlocked')
		return True

	def getLockStatus(self):
		config = json.loads(open(CONFIG_PATH, 'r').read())
		access_token = config['accessToken']
		lock_id = config['lockId']
		r = requests.get(LOCK_API_ROOT + '/locks/' + lock_id + '?access_token=' + access_token)
		return r.json()

	def unlock(self):
		config = json.loads(open(CONFIG_PATH, 'r').read())
		access_token = config['accessToken']
		lock_id = config['lockId']
		r = requests.put(LOCK_API_ROOT + '/locks/' + lock_id + '?access_token=' + access_token + '&state=unlock')
		if 'status' in r.json() and r.json()['status'] == 'error':
			return False
		return r.json()['state'] == 'unlock'

	def lock(self):
		config = json.loads(open(CONFIG_PATH, 'r').read())
		access_token = config['accessToken']
		lock_id = config['lockId']
		r = requests.put(LOCK_API_ROOT + '/locks/' + lock_id + '?access_token=' + access_token + '&state=lock')
		if 'status' in r.json() and r.json()['status'] == 'error':
			return False
		return r.json()['state'] == 'lock'

	def askHostPermission(self):
		self.messageManager.sendVerificationMessage()

	def getLockIdByAccessToken(self, accessToken):
		r = requests.get(LOCK_API_ROOT + '/locks/?access_token=' + accessToken)
		if 'status' in r.json() and r.json()['status'] == 'error':
			return False
		r = r.json()
		for i in r:
			if i['name'] != "Virtual Lockitron":
				return i['id']
		return None

#
# a = LockManager()
# print(a.getLockIdByAccessToken('24d8392e366b60f845da4c0f44c38183226cedcd41bfc7ea0c34837e98ed9c62'))
