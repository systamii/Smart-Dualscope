import astropy
import requests
import gphoto2 as gp
import json
import env
from astropy.coordinates import SkyCoord
from astropy.coordinates.name_resolve import NameResolveError
import astropy.units as u
import numpy as np
import pandas as pd
import time
import camera_config
import os
import glob
import cv2
import gphoto2 as gp

    

#1.0 - Take a picture w/ the camera and save it to a file in the directory
my_camera = gp.Camera()
def take_photo(camera):
    camera_connected = False
    while(not camera_connected):
        try:
            camera.init()
            camera_connected = True
            time.sleep(2)
        except gp.GPhoto2Error as ex:
            print("Camera not detected. Please ensure your device is turned on and connected.")
            time.sleep(1.5)
    img_path = my_camera.capture(gp.GP_CAPTURE_IMAGE)
    camera_file = my_camera.file_get(img_path.folder, img_path.name,gp.GP_FILE_TYPE_NORMAL)
    camera_file.save("/Users/jchandler/Desktop/PIE/photos/brehhhhhh.jpg")

take_photo(my_camera)

    

























    

#1.1- Login to the Astrometry API
astrometry_login_request = (requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": env.astrometry_api_key})})).json()
session_key = astrometry_login_request["session"]
response_data = json.dumps(astrometry_login_request)
#1.2- Upload sample file to the Astrometry API
upload_url = "http://nova.astrometry.net/api/upload"
files = {'file': open('photos/IMG_9104.png', 'rb')} #REPLACE WITH PHOTO OUTPUT FROM CAMERA
data = {'request-json': json.dumps({'session': session_key})}
astrometry_upload_request = requests.post(upload_url, data=data, files=files).json()

#1.3 Get results from the file upload
job_complete = False
attempt_counter = 0
submission_id = astrometry_upload_request["subid"]
print("Submission ID: " + str(submission_id))
while not job_complete:
    job_submission = (requests.get("http://nova.astrometry.net/api/submissions/"+str(submission_id)).json())
    if( (len(job_submission["jobs"]) > 0) and (len(job_submission["job_calibrations"]) > 0) and (job_submission["jobs"][0] is not None) and (job_submission["processing_finished"] is not None)):
        job_complete = True
        print("Job complete!")
        time.sleep(1.5)
        break
    else:
        if(attempt_counter >= 10):
            print("An error occurred. Please try again.")
        else:
            print("Job still in progress. Retrying...")
            time.sleep(2.5)
        attempt_counter += 1
job_id = job_submission["jobs"][0]
print("Job ID: " + str(job_id))
processed_image_data = (requests.get("http://nova.astrometry.net/api/jobs/"+str(job_id)+"/info/")).json()
current_ra = processed_image_data["calibration"]["ra"] * u.deg
current_dec = processed_image_data["calibration"]["dec"] * u.deg
print("Current RA: " + str(current_ra))
print("Current dec: " + str(current_dec))
# Phase 2: User-Inputted Stellar Object Lookup
mode_selected = False
while not mode_selected:
        mode_toggle = input("Would you like to use a preset capture mode? (y/n) ")
        if(mode_toggle == "y"):
            while mode_selected is False:
                try:
                    mode_selection = input("What preset would you like to use? ")
                    print(set_capture_mode(mode_selection))
                    mode_selected = True
                except ValueError:
                    print("Unknown mode. Please try again.")
                    time.sleep(1.5)

        elif(mode_toggle == "n"):
            break
url_obtained = False
while not url_obtained:
    try:
        stellar_obj = input("Please enter the name of your desired stellar object: ")
        url_obtained = True
        obj_coords = astropy.coordinates.get_icrs_coordinates(stellar_obj)
    except NameResolveError:
        print("Invalid object name. Please try again.")
        url_obtained = False
target_ra = obj_coords.ra * u.deg
target_dec = obj_coords.dec * u.deg
print("Target Right Ascension: "+str(target_ra))
print("target Declination: "+str(target_dec))


# Given the coordinates of an object, move motors until you reach the object & track it as the night goes on

#2.0 Calibrate the motors. 1 Motor step = 1.8 degrees, so equate that to a change in RA/Declination.

# Alternatively: We know that the Earth moves 365 degrees in 23h 56m; As such, it moves roughly 0.25 degrees each minute

#0.0 - Helper functions
def set_capture_mode(input):
    if (input == "Default" or "default"):
        return "default selected" #we gotta add functionality to this
    elif (input == "Trail" or "trail"):
        return "trail selected"   #we gotta add functionality to this
    else:
        raise ValueError("Mode not recognized.")