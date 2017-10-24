import requests
import json
import os
import time
import SystemManager
import MessageManager

class LockManager:
	def __init__(self):
		self.systemManager = SystemManager.SystemManager()
		self.messageManager = MessageManager.MessageManager()

	def doUnlock(self, user):
		# Do unlock

		#then log & send message to host
		self.messageManager.sendMessage("Welcome home, " + user, self.messageManager.getHostPhone())
		self.systemManager.writeSystemLog('User ' + user + ' unlocked')
		return True
