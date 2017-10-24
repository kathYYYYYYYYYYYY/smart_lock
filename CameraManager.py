import requests
import json
import os
import time

AUTHY_API_KEY = 'Qz9ObWcxCdSkxjLqvdILQq1yfSAinpGR'

class MessageManager:
	def __init__(self):
		pass

	def sendVerificationMessage(self):
		self.sendMessage(HOST_PHONE_NUMBER)
    def sendMessage(self, phone, via = 'sms', country_code = '1', API_KEY = AUTHY_API_KEY):
        r = requests.post("https://api.authy.com/protected/json/phones/verification/start?api_key=" + API_KEY
            , data={'via': via, 'phone_number': phone, 'country_code': country_code})
        if int(r.status_code) == 200:
            return {'status': 0}
        else:
            return {'status': 1, 'message': json.loads(r.text)['message']}