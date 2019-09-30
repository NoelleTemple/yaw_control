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
p.start(0.5)

#original heading
og_heading, roll, pitch = bno.read_euler()
#where do you want to go?
degrees = 60
#clockwise if true, counter clockwise if false
cw = true

while True:
	GPIO.setwarnings(False)
	heading, roll, pitch = bno.read_euler()
	sys, gyro, accel, mag = bno.get_calibration_status()
	print('Heading = {0:0.2F}'.format(heading))
	if cw == true:
		#set servo all the way to the left
		dc = 2.5
		new_heading = og_heading + degrees
		if new_heading > 360:
			des_heading = new_heading-360
		else:
			des_heading = new_heading
		x = True
		while x == True:
			p.ChangeDutyCycle(dc)
			time.sleep(0.25)
			heading, roll, pitch = bno.read_euler()
			if heading < des_heading+5 && heading > des_heading-5:
				x=False
			else:
				dc=dc+1
			#need an exception if it doesn't catch it (when does it just pass,
			#could change step size and go back instead of looking for certain point
			#what happens if it just never reads where it's in those bounds?
		print('duty cycle: {}'.format(dc))
	else:
		dc = 12.5
		new_heading = og_heading-degress
		if new_heading < 0:
			des_heading = new_heading + 360
		else:
			des_heading = new_heading
		x = True
		while x == True:
			p.ChangeDutyCycle(dc)
			time.sleep(0.25)
			heading, roll, pitch = bno.read_euler()
			if heading < des_heading+5 && heading > des_heading-5:
				x = False
			else:
				dc = dc-1
			#need that exception from earlier here.
GPIO.cleanup()

#also need an exception to address if des_heading is out of servo range (preferably without 
#moving the servos to the edges to find them-servo will go to one end, calculate other end with that value?
#will be an approximation so give 10 degree buffer zone? (not the most accurate detection method)
