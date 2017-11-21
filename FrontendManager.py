import requests
import json
import os
import time
from flask import logging, Flask, Response, jsonify, request, url_for, redirect, send_file, render_template, session, flash, send_from_directory
import LockManager
import base64
import string
import random

TOKEN_EXPIRED = 3 * 60

class FrontendManager:
    def __init__(self):
        self.lockManager = LockManager.LockManager()

    def getAdminPanel(self, receivingToken):
        if not self.verifyToken(receivingToken):
            return self.getFailPage('Authentication Failed')
        return render_template("admin.html", token = receivingToken)

    def getLocalToken(self):
        token_cache = json.loads(open('json/token.json', 'r').read())
        current_time = int(time.time())
        if token_cache and 'token' in token_cache and (token_cache['updatedTime'] + TOKEN_EXPIRED > current_time):
            return token_cache['token']
        else:
            return None

    def getSetupPage(self):
        return render_template("setup.html")

    def getFailPage(self, message):
        return render_template("fail.html", message = message)

    def verifyToken(self, receivingToken):
        return self.getLocalToken() != None and receivingToken == self.getLocalToken()

    def doAction(self, action, receivingToken):
        if not self.verifyToken(receivingToken):
            return {'status': 1, 'message': "Authentication Failed"}
        if action == 'unlock':
            # Do unlock
            if self.lockManager.doUnlock('host(via admin page)'):
                return {'status': 0}
            else:
                return {'status': 1, 'message': "Failed to unlock, connection issue"}
        elif action == 'call':
            # Do call police
            return {'status': 0}

    def doSetup(self, phoneNumber, name, pic, accessToken):
        # Save conf, phonen, etc
        f = open('json/config', 'w')
        lockId = self.lockManager.getLockIdByAccessToken(accessToken)
        if not lockId:
            return {'status': 1, 'message': "Lock not found, please make sure lock is set up."}
        dic = {'phone': phoneNumber, 'accessToken': accessToken, 'lockId': lockId}
        f.write(json.dumps(dic))
        f.close()

        # Save images
        path = 'images/' + name

        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + self.getRandomString() +".png", "wb") as fh:
            fh.write(base64.b64decode(pic))
        return {'status': 0}

    def getAddFacesPage(self, token):
        if not self.verifyToken(token):
            return {'status': 1, 'message': "Authentication Failed"}
        return render_template("add_faces.html", token = token)

    def getRandomString(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def doAddFace(self, token, pic, name):
        path = 'images/' + name
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + self.getRandomString() + ".png", "wb") as fh:
            fh.write(base64.b64decode(pic))
        return {'status': 0}
