import logging
import sys
import time
import RPi.GPIO as GPIO
from servocntl_pkg import servo
from Adafruit_BNO055 import BNO055

su=servo(description="change to desired heading", boardpin = 35, frequency = 50)
su.setup()

bno = BNO055.BNO055(address=0x29)

if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
	logging.basicConfig(level=logging.DEBUG)

if not bno.begin():
	raise RuntimeError('Failed to initialize BNO055!  Is the sensor connected?')

status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))

if status == 0x01:
	print('System error: {0}'.format(error))
	print('See datasheet section 4.3.59 for the meaning.')
print('Reading BNO055 Heading.  Press Cntl-C to quit...')
p=GPIO.PWM(su.boardpin, su.frequency)
p.start(0)
cnt=0
while True:
	GPIO.setwarnings(False)
	heading, roll, pitch = bno.read_euler()
	sys, gyro, accel, mag = bno.get_calibration_status()
	print('Heading = {0:0.2F}'.format(heading))
	cnt=cnt+1
	p.ChangeDutyCycle(cnt)
	print('Duty Cycle = {}'.format(cnt)) 
	time.sleep(1)

GPIO.cleanup()
