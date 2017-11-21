import requests
import json
import os
import time
from twilio.rest import Client
import binascii

account_sid = "AC3db735ad8d7d473be29935a424f53642"
auth_token = "d5e73e1ff1cc0c8a1922c3de187364b5"

HOST_PHONE_NUMBER = '+14168766678'
TOKEN_EXPIRED = 3 * 60

class MessageManager:
    def __init__(self):
        self.client = Client(account_sid, auth_token)

    def sendVerificationMessage(self):
        self.sendMessage(self.messageTemplateFormatter(), self.getHostPhone())

    def getHostPhone(self):
        config = json.loads(open('json/config', 'rb').read().decode("utf-8"))
        return config['phone']

    def sendMessage(self, message, target):
        message = self.client.api.account.messages.create(to= target,
                                                     from_= "+15817052316",
                                                     body= message)

    def messageTemplateFormatter(self):
        front_end_url = 'FONTEND_URL?token=' + self.getAccessToken()
        return 'Someone is trying to access  your locker, click ' + front_end_url + ' to admin panel.'

    def getAccessToken(self):
        '''
        Get a temporarily access token for admin panel when sending a message, expiried in 3 mins
        '''
        token_cache = json.loads(open('json/token.json', 'rb').read().decode("utf-8"))
        current_time = int(time.time())

        if (not token_cache) or (token_cache['updatedTime'] + TOKEN_EXPIRED < current_time):
            # 若json文件不存在或已过期
            newToken = str(binascii.hexlify(os.urandom(16)), 'ascii')
            token_cache = {"token": newToken, 'updatedTime': int(time.time())}
            with open('json/token.json', 'w') as outfile:
                json.dump(token_cache, outfile)
        return token_cache['token']

'''
a = MessageManager()
a.sendVerificationMessage()
'''
