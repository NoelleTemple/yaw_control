from servo_pi.servo import Servo
from Adafruit_BNO055 import BNO055
import time
import sys


def main(argv):
    head_goal = float(argv[0])

    servo = Servo(35)

    bno = BNO055.BNO055(address=0x29)

    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055!  Is the sensor connected?')

    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))

    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')
    print('Reading BNO055 Heading.  Press Cntl-C to quit...')

    pos = 90
    servo.set_position(pos)

    while True:
        cur_heading, _, _ = bno.read_euler()
        minval = abs((cur_heading - pos) % 360)
        maxval = abs((cur_heading + (180 - pos)) % 360)

        if minval < maxval:
            mode = 0x00
        else:
            mode = 0x01

        if ((cur_heading - 15) < head_goal) & ((cur_heading + 15) > head_goal):
            pos = pos
            print("goal achieved")
        elif mode == 0x00:
            if head_goal > maxval or head_goal < minval:
                print("goal is out of range")
            elif head_goal < cur_heading:
                pos -= 10
            elif head_goal > cur_heading:
                pos += 10
        else:
            if (head_goal > maxval) and (head_goal < minval):
                print("goal is out of range")
            elif (head_goal < maxval) & (cur_heading < maxval):
                if (head_goal < cur_heading):
                    pos -= 10
                elif (head_goal > cur_heading):
                    pos += 10
            elif (head_goal > minval) & (cur_heading > minval):
                if (head_goal < cur_heading):
                    pos -= 10
                elif (head_goal > cur_heading):
                    pos += 10
            elif (head_goal < maxval) & (cur_heading > maxval):
                pos += 10
            elif (head_goal > minval) & (cur_heading < minval):
                pos -= 10
            else:
		pass

        servo.set_position(pos)
        time.sleep(.1)
        print("heading: {}    head_goal: {}".format(cur_heading, head_goal))

if __name__ == "__main__":
    main(sys.argv[1:])
