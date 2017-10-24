import requests
import json
import os
import time


class FacialRecognitionManager:
    def __init__(self):
        pass
    def getUserImages(self):
        IMAGE_ROOT = './images/'
        result = {}
        for user in os.listdir(IMAGE_ROOT):
            if user != '.DS_Store':
                for pic in os.listdir(IMAGE_ROOT + user):
                    if os.path.isfile(IMAGE_ROOT + user + '/' + pic) and pic != '.DS_Store':
                        url = IMAGE_ROOT + user + '/' + pic
                        if user not in result:
                            result[user] = [url]
                        else:
                            result[user].append(url)
        return result

    def doMatchFace(self, detecting_img):
        '''
        Compare detecting_img with faces in database, if match result meets the threshhold, return the matching name and image url
        '''
        all_user = self.getUserImages()
        THRESH_HOLD = 50
        for name in all_user:
            for image in all_user[name]:
                # Now match detecting_img and image, to get score
                score = self.getSimilarityBetweenFaces(image, detecting_img)
        return

    def getSimilarityBetweenFaces(self, face1, face2):
        return 0

    def startRecognition(self, cam_source):
        pass

'''
a = FacialRecognitionManager()
a.getUserImages()
'''
