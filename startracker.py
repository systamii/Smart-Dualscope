import astropy
import requests
import json
import env
from astropy.coordinates import SkyCoord
from astropy.coordinates.name_resolve import NameResolveError
import numpy as np
import pandas as pd
import time
#Phase One: Telescope Calibration

# ---GOALS----
    #Take a Picture of the current surroundings [IN PROGRESS]
    #Plate-Solve to get rough estimate of where we are  [COMPLETED!]

#1.0 - Take a picture w/ the camera and save it to a file in the directory

#1.1- Login to the Astrometry API
astrometry_login_request = (requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": env.astrometry_api_key})})).json()
session_key = astrometry_login_request["session"]
response_data = json.dumps(astrometry_login_request)
#1.2- Upload sample file to the Astrometry API
upload_url = "http://nova.astrometry.net/api/upload"
files = {'file': open('photos/IMG_9102.png', 'rb')} #REPLACE WITH PHOTO OUTPUT FROM CAMERA
data = {'request-json': json.dumps({'session': session_key})}
astrometry_upload_request = requests.post(upload_url, data=data, files=files).json()
#1.3 Get results from the file upload
time.sleep(10) # WAIT--- It takes time for the upload to complete
submission_id = astrometry_upload_request["subid"]
print("Submission ID: " + str(submission_id))
job_submission = (requests.post("http://nova.astrometry.net/api/submissions/"+str(submission_id)).json())
print(job_submission)
job_id = job_submission["jobs"][0]
print("Job ID: " + str(job_id))
processed_image_data = (requests.post("http://nova.astrometry.net/api/jobs/"+str(job_id)+"/info/")).json()
current_ra = processed_image_data["calibration"]["ra"]
current_dec = processed_image_data["calibration"]["dec"]
print("Current RA: " + str(current_ra))
print("Current dec: " + str(current_dec))


# Phase 2: User-Inputted Stellar Object Lookup
url_obtained = False    
while not url_obtained:
    try:
        #stellar_obj = input("Please enter the name of your desired stellar object: ")
        stellar_obj = "Polaris"
        url_obtained = True
        obj_coords = astropy.coordinates.get_icrs_coordinates(stellar_obj)
    except NameResolveError:
        print("Invalid object name. Please try again.")
        url_obtained = False
target_ra = obj_coords.ra
target_dec = obj_coords.dec
print(target_ra, target_dec)


# Given the coordinates of an object, move motors until you reach the object & track it as the night goes on

#2.0 Calibrate the motors to a specific RA. 1 Motor step = 1.8 degrees, so equate that to a change in RA/Declination.





# CODE VAULT
# Save the dictionary to a JSON file
#with open("data.json", "w") as f:
#    json.dump(processed_image_data, f, indent=4) # indent for pretty-printing

# Load the dictionary back from the JSON file
#with open("data.json", "r") as f:
#    loaded_dict = json.load(f)