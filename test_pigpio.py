import pigpio
import time

pi = pigpio.pi()

# ---------------- MOTOR CONFIG ---------------- #

PAN_PULSE = 20
PAN_DIR   = 21

TILT_PULSE = 23
TILT_DIR   = 24

FULL_STEPS_PER_REV = 200
MICROSTEP = 1/2
STEPS_PER_REV = FULL_STEPS_PER_REV * MICROSTEP

pi.set_mode(PAN_PULSE,  pigpio.OUTPUT)
pi.set_mode(PAN_DIR,    pigpio.OUTPUT)
pi.set_mode(TILT_PULSE, pigpio.OUTPUT)
pi.set_mode(TILT_DIR,   pigpio.OUTPUT)

def build_wave(pulse_pin, rpm, revolutions, direction):
    pi.write(direction[0], direction[1])

    # steps_per_sec = rpm * STEPS_PER_REV / 60.0
    # period_us = int((1.0 / steps_per_sec) * 1_000_000)
    total_steps = int(revolutions * STEPS_PER_REV)

    pulse_high_us = 10      # DM542 requires >= 2.5 µs
    pulse_low_us = 10

    pulses = []
    for _ in range(total_steps):
        # pulses.append(pigpio.pulse(1<<pulse_pin, 0, period_us//2))
        # pulses.append(pigpio.pulse(0, 1<<pulse_pin, period_us//2))
        pulses.append(pigpio.pulse(1<<pulse_pin, 0, pulse_high_us))
        pulses.append(pigpio.pulse(0, 1<<pulse_pin, pulse_low_us))

    pi.wave_add_generic(pulses)
    return pi.wave_create()


# ------------------------------------------------ #
# RUN PAN MOTOR FIRST
# ------------------------------------------------ #

pi.wave_clear()

PAN_RPM = 15
REV = 2

pan_wave = build_wave(PAN_PULSE, PAN_RPM, REV, (PAN_DIR, 1))

pi.wave_send_once(pan_wave)

while pi.wave_tx_busy():
    time.sleep(0.01)

pi.wave_delete(pan_wave)


# ------------------------------------------------ #
# THEN RUN TILT MOTOR
# ------------------------------------------------ #

TILT_RPM = 15

tilt_wave = build_wave(TILT_PULSE, TILT_RPM, REV, (TILT_DIR, 0))

pi.wave_send_once(tilt_wave)

while pi.wave_tx_busy():
    time.sleep(0.01)

pi.wave_delete(tilt_wave)


# ------------------------------------------------ #
# CLEANUP
# ------------------------------------------------ #

pi.wave_clear()
pi.stop()
