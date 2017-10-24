#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import logging, Flask, Response, jsonify, request, url_for, redirect, send_file, render_template, session, flash, send_from_directory
import sys
import json
import time
import random
import urllib.parse

import FrontendManager
import SystemManager


from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

frontendManager = FrontendManager.FrontendManager()
systemManager = SystemManager.SystemManager()

@app.route("/auth/<token>")
def auth_page(token):
    return frontendManager.getAdminPanel(token)

@app.route("/setup")
def setup_page():
    if not systemManager.ifFinishedSetup():
        return frontendManager.getSetupPage()
    else:
        return frontendManager.getFailPage('Already Setup')

# REST API
@app.route("/action/<action>", methods=['POST'])
def doAction(action):
    token = request.form.get("token")
    return jsonify(frontendManager.doAction(action.lower(), token))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8083, debug=True, threaded=True)
