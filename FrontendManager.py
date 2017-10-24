import requests
import json
import os
import time
from flask import logging, Flask, Response, jsonify, request, url_for, redirect, send_file, render_template, session, flash, send_from_directory

TOKEN_EXPIRED = 3 * 60

class FrontendManager:
    def __init__(self):
        pass

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
            return {'status': 0}
        elif action == 'call':
            # Do call police
            return {'status': 0}
