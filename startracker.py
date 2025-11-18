import astropy
import requests
import gphoto2 as gp
import json
import env
import time
from astropy.coordinates.name_resolve import NameResolveError
import astropy.units as u
import os

PRESET_MODES = ["Manual", "Nebula"]

def reset(camera):
    """
    Resets the Camera between photos. Takes a camera as a parameter, and returns the now resetted camera object.
    """
    camera.exit()
    camera = gp.Camera()
    camera.init()
    return camera


def take_photo(camera):
    """
    exactly what it sounds like. Takes a camera as a parameter. Doesn't return anything
    """
    camera_connected = False
    while(not camera_connected):
        try:
            camera.init()
            camera_connected = True
            time.sleep(2)
        except gp.GPhoto2Error as ex:
            print("Camera not detected. Please ensure your device is turned on and connected.")
            time.sleep(1.5)
    img_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    camera_file = camera.file_get(img_path.folder, img_path.name, gp.GP_FILE_TYPE_NORMAL)
    filepath = "/Users/jchandler/Desktop/PIE/photos/" + str(img_path.name)
    camera_file.save(filepath)
    camera.exit()
    return (filepath)


def set_capture_mode():
    mode_selected = False
    while not mode_selected:
            mode_toggle = input("Would you like to use a preset capture mode? (y/n) ")
            if(mode_toggle == "y"):
                while mode_selected is False:
                        mode_selection = input("What preset would you like to use? ")
                        if(mode_selection in PRESET_MODES):
                            mode_selected = True
                            break
                        else:
                            print("Unknown mode. Please try again.")
            elif(mode_toggle == "n"):
                break

def plate_solver(ref_photo):

    # #1.1- Login to the Astrometry API
    astrometry_login_request = (requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": env.astrometry_api_key})})).json()
    session_key = astrometry_login_request["session"]

    #1.2- Upload sample file to the Astrometry API
    files = {'file': open("photos/IMG_9104.png", 'rb')}
    data = {'request-json': json.dumps({'session': session_key})}
    astrometry_upload_request = requests.post(env.upload_url, data=data, files=files).json()
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
                break
            else:
                print("Job still in progress. Retrying...")
                time.sleep(2.5)
            attempt_counter += 1
    job_id = job_submission["jobs"][0]
    print("Job ID: " + str(job_id))
    processed_image_data = (requests.get("http://nova.astrometry.net/api/jobs/"+str(job_id)+"/info/")).json()
    current_ra = processed_image_data["calibration"]["ra"] * u.deg
    current_dec = processed_image_data["calibration"]["dec"] * u.deg
    return current_ra, current_dec

# Phase 2: User-Inputted Stellar Object Lookup
def object_finder():
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
    return target_ra, target_dec


# Given the coordinates of an object, move motors until you reach the object & track it as the night goes on

#2.0 Calibrate the motors. 1 Motor step = 1.8 degrees, so equate that to a change in RA/Declination.

# Alternatively: We know that the Earth moves 365 degrees in 23h 56m; As such, it moves roughly 0.25 degrees each minute

my_camera = gp.Camera()
set_capture_mode()
my_cal_photo = take_photo(my_camera)
calibration_ra, calibration_dec = plate_solver(my_cal_photo)
target_ra, target_dec = object_finder()
print("Target Right Ascension: "+str(target_ra))
print("target Declination: "+str(target_dec))
def move_to_target(target_ra,target_dec):
    while target_ra != calibration_ra:
        if calibration_ra > target_ra:
            print("move motors clockwise")
        elif calibration_ra < target_ra:
            print("move motors counter-clockwise")
        else:
            break
    while target_dec != calibration_dec:
        if target_dec > calibration_dec:
            print("move motors up")
        if target_dec < calibration_dec:
            print("move motors down")

