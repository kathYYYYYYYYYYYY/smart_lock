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

#from Camera import Camera

from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG


frontendManager = FrontendManager.FrontendManager()
systemManager = SystemManager.SystemManager()

@app.route("/add_faces/<token>", methods=['POST', 'GET'])
def add_faces(token):
    if request.method == 'POST':
        name = request.form.get("name")
        pic = request.form.get("pic").split(',')[-1]
        accessToken = token
        return jsonify(frontendManager.doAddFace(name, pic, accessToken))

    return frontendManager.getAddFacesPage(token)

@app.route("/auth/<token>")
def auth_page(token):
    return frontendManager.getAdminPanel(token)

@app.route("/setup", methods=['POST', 'GET'])
def setup_page():
    if request.method == 'POST':
        phoneNumber = request.form.get("phoneNumber")
        name = request.form.get("name")
        pic = request.form.get("pic").split(',')[-1]
        accessToken = request.form.get("accessToken")
        return jsonify(frontendManager.doSetup(phoneNumber, name, pic, accessToken))

    if not systemManager.ifFinishedSetup():
        return frontendManager.getSetupPage()
    else:
        return frontendManager.getFailPage('Already Setup')

# REST API
@app.route("/action/<action>", methods=['POST'])
def doAction(action):
    token = request.form.get("token")
    return jsonify(frontendManager.doAction(action.lower(), token))

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8083, debug=True, threaded=True)
