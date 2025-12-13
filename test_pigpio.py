import pigpio
import time

pi = pigpio.pi()

# ---------------- MOTOR CONFIG ---------------- #

PAN_PULSE = 20
PAN_DIR   = 21

TILT_PULSE = 23
TILT_DIR   = 24

CW  = 1
CCW = 0

PAN_GEAR_RATIO  = 180
TILT_GEAR_RATIO = 5

FULL_STEPS_PER_REV = 200
MICROSTEP = 1

PAN_STEPS_PER_OUTPUT_REV  = FULL_STEPS_PER_REV * MICROSTEP * PAN_GEAR_RATIO
TILT_STEPS_PER_OUTPUT_REV = FULL_STEPS_PER_REV * MICROSTEP * TILT_GEAR_RATIO

MAX_STEPS_PER_WAVE = 1000
PULSE_HIGH_US = 5

pi.set_mode(PAN_PULSE,  pigpio.OUTPUT)
pi.set_mode(PAN_DIR,    pigpio.OUTPUT)
pi.set_mode(TILT_PULSE, pigpio.OUTPUT)
pi.set_mode(TILT_DIR,   pigpio.OUTPUT)

# ---------------------- Generate PWM waves ---------------------- #

def run_motor(pulse_pin, rpm, revolutions, direction, steps_per_output_rev):
    pi.write(direction[0], direction[1])
    time.sleep(0.00001)

    steps_per_sec = rpm * steps_per_output_rev / 60.0
    period_us = int(1_000_000 / steps_per_sec)

    total_steps = int(revolutions * steps_per_output_rev)
    print(f"{total_steps} steps to take!")

    PULSE_HIGH_US = 5
    pulse_low_us = period_us - PULSE_HIGH_US

    MAX_STEPS_PER_WAVE = 1000

    steps_remaining = total_steps

    # Divide full wave into smaller ones
    while steps_remaining > 0:
        steps_this_wave = min(steps_remaining, MAX_STEPS_PER_WAVE)

        pi.wave_clear()

        pulses = []
        for _ in range(steps_this_wave):
            pulses.append(pigpio.pulse(1 << pulse_pin, 0, PULSE_HIGH_US))
            pulses.append(pigpio.pulse(0, 1 << pulse_pin, pulse_low_us))

        pi.wave_add_generic(pulses)
        wave_id = pi.wave_create()

        pi.wave_send_once(wave_id)
        while pi.wave_tx_busy():
            time.sleep(0.002)

        pi.wave_delete(wave_id)

        steps_remaining -= steps_this_wave
        print(f"{steps_remaining} steps remaining...")



# ------------------------------------------------ #
# RUN MOTORS
# ------------------------------------------------ #

pi.wave_clear()

try:
    PAN_RPM = 0.05 # RPM of cycloidal drive --> PAN_RPM*180 = RPM of pan motor
    PAN_REV = 0.01 # REV of cycloidal drive --> PAN_REV*180 = REV of pan motor
    run_motor(PAN_PULSE, PAN_RPM, PAN_REV, (PAN_DIR, 1), PAN_STEPS_PER_OUTPUT_REV)
    print(f"Pan motor running at {PAN_RPM} RPM for {PAN_REV} revolutions.")

    TILT_RPM = 0.5 # RPM of gear belt --> TILT_RPM*180 = RPM of tilt motor
    TILT_REV = 1 # RPM of gear belt --> TILT_RPM*180 = RPM of tilt motor
    run_motor(TILT_PULSE, TILT_RPM, TILT_REV, (TILT_DIR, 0), TILT_STEPS_PER_OUTPUT_REV)
    print(f"Pan motor running at {TILT_RPM} RPM for {TILT_REV} revolutions.")

except KeyboardInterrupt:
    print("\nCtrl+C detected — stopping motors immediately")

finally:
    pi.wave_tx_stop()    # stop active wave immediately
    pi.wave_clear()      # clear DMA
    pi.write(PAN_PULSE, 0)
    pi.write(TILT_PULSE, 0)
    pi.stop()

# ------------------------------------------------ #
# CLEANUP
# ------------------------------------------------ #

pi.wave_clear()
pi.stop()
