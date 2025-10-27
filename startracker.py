import astropy
import requests
import json
import env
from astropy.coordinates import SkyCoord
from astropy.coordinates.name_resolve import NameResolveError
import numpy as np
import pandas as pd
#Phase One: Telescope Calibration
# ---GOALS----
    #Take a Picture of the current surroundings
    #Plate-Solve to get rough estimate of where we are
#1.0 - Take a picture w/ the camera and save it to a file in the directory

#1.1- Login to the Astrometry API
astrometry_login_request = requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": env.astrometry_api_key})})
response_data = json.loads(astrometry_login_request)

#1.2- Upload sample file to the Astrometry API
upload_url = "http://nova.astrometry.net/api/upload"
files = {'file': open('IMG_9102.png', 'rb')} #uses a placeholder file rn
data = {'request-json': json.dumps({'session': "loxo54w20t11wvyx5qqb86e3nt5bbl43"})}






# Phase 2: User-Inputted Stellar Object Lookup
url_obtained = False
while not url_obtained:
    try:
        #stellar_obj = input("Please enter the name of your desired stellar object: ")
        stellar_obj = "Vega"
        url_obtained = True
        obj_coords = astropy.coordinates.get_icrs_coordinates(stellar_obj)
    except NameResolveError:
        print("Invalid object name. Please try again.")
        url_obtained = False
right_ascension = obj_coords.ra
declination = obj_coords.dec
print(right_ascension, declination)


# Given the coordinates of an object, move motors until you reach the object & track it as the night goes on
