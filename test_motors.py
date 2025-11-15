from time import sleep
import RPi.GPIO as gpio

pan_direction   = 20
pan_pulse       = 21
tilt_direction  = 23 
tilt_pulse      = 24
cw_direction    = 0
ccw_direction   = 1

gpio.setmode(gpio.BCM)
gpio.setup(pan_direction, gpio.OUT)
gpio.setup(pan_pulse, gpio.OUT)
gpio.setup(tilt_direction, gpio.OUT)
gpio.setup(tilt_pulse, gpio.OUT)

tilt_steps = 0

try:
    while True:
        # if tilt_steps <= 100:
        #     print(f'Step: {tilt_steps}')
        #     sleep(.05)
        #     gpio.output(tilt_direction,ccw_direction)
        #     gpio.output(tilt_pulse,gpio.HIGH)
        #     sleep(.0001)
        #     gpio.output(tilt_pulse,gpio.LOW)
        #     sleep(.0001)
        #     tilt_steps+=1
        # else:
        #     pass
        # Need to implement a push switch so that the camera lens doesn't crash into the pan mechanism
    
        sleep(.0001)
        gpio.output(pan_direction,cw_direction)
        gpio.output(pan_pulse,gpio.HIGH)
        sleep(.0001)
        gpio.output(pan_pulse,gpio.LOW)
        sleep(.0001)




except KeyboardInterrupt:
    gpio.cleanup()