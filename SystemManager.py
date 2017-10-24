import requests
import json
import os
import time
from flask import logging, Flask, Response, jsonify, request, url_for, redirect, send_file, render_template, session, flash, send_from_directory

TOKEN_EXPIRED = 3 * 60

SYS_LOG_PATH = 'json/log.json'

class SystemManager:
    def __init__(self):
        pass

    def ifFinishedSetup(self):
        import os.path
        return os.path.isfile('json/setup.lock')

    def setFinishedSetup(self):
        if not self.ifFinishedSetup():
            file = open('json/setup.lock', 'w')


    def saveSystemConfig(self, phoneNumber, photos):
        # Save conf, phonen, etc
        f = open('json/config', 'w')
        dic = {'phone': phoneNumber}

        # Save images
        images_path = []
        for i in photos:
            images_path.append(i) # add path
            # save i to images

        dic['images'] = images_path
        f.write(json.dumps(dic))
        f.close()
        return {'status': 0}

    def getSystemLog(self):
        log = json.loads(open(SYS_LOG_PATH, 'r').read())
        return log

    def writeSystemLog(self, event):
        log = self.getSystemLog()
        newLog = {
            'time': int(time.time()),
            'event': event
        }
        log.append(newLog)
        f = open(SYS_LOG_PATH, 'w')
        f.write(json.dumps(log))
        f.close()
        return
