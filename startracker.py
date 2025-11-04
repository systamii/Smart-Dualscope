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
#                        ------------------PHASE ONE: TELESCOPE CALIBRATION-----------------------

# ---GOALS----
    #Take a Picture of the current surroundings [IN PROGRESS]
    #Plate-Solve said picture to get rough estimate of where we are  [COMPLETED!]
    #Allow user to select a target to observe [COMPLETED!]
    #Calibrate motors & move Telescope to the target [IN PROGRESS]

#1.0 - Take a picture w/ the camera and save it to a file in the directory
myCamera = gp.Camera()
myCamera.init()

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