# count_pulses.py
import pigpio, time

STEP = 20
DIR  = 21

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpio not connected")

pi.set_mode(STEP, pigpio.OUTPUT)
pi.set_mode(DIR, pigpio.OUTPUT)

pi.write(DIR, 0)
time.sleep(0.1)# count_pulses.py
import pigpio, time

STEP = 20
DIR  = 21

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpio not connected")

pi.set_mode(STEP, pigpio.OUTPUT)
pi.set_mode(DIR, pigpio.OUTPUT)

pi.write(DIR, 0)
time.sleep(0.1)

# Pick counts to test. We'll do 200, 400, 800, 1600
tests = [36000]
high = 0.01   # 50 ms HIGH
low  = 0.01   # 50 ms LOW

for cnt in tests:
    print(f"\nSending {cnt} pulses (50ms H / 50ms L). Watch rotation.")
    for i in range(cnt):
        pi.write(STEP, 1)
        time.sleep(high)
        pi.write(STEP, 0)
        time.sleep(low)
    print("done — observe motor position now, then press Enter to continue")
    input()

pi.stop()
print("all tests done")

# Pick counts to test. We'll do 200, 400, 800, 1600
tests = [36000]
high = 0.01   # 50 ms HIGH
low  = 0.01   # 50 ms LOW

for cnt in tests:
    print(f"\nSending {cnt} pulses (50ms H / 50ms L). Watch rotation.")
    for i in range(cnt):
        pi.write(STEP, 1)
        time.sleep(high)
        pi.write(STEP, 0)
        time.sleep(low)
    print("done — observe motor position now, then press Enter to continue")
    input()

pi.stop()
print("all tests done")