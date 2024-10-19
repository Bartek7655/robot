import time

import board
import busio
from adafruit_pca9685 import PCA9685


class ServoController:
    def __init__(self, servo_motor, home_position, steps_slow=150, steps_fast=50, max_degrees=180, name=''):
        self.servo = servo_motor
        self.current_angle = self.servo.angle
        self.steps_slow = steps_slow
        self.steps_fast = steps_fast
        self.max_degrees = max_degrees
        self.name = name
        self.home_position = home_position

    def move_slowly(self, end_angle, duration=1.5):
        steps = self.steps_slow
        step_duration = duration / steps
        angle_step = (end_angle - self.current_angle) / steps

        for _ in range(steps):
            self.current_angle += angle_step
            self.servo.angle = max(0, min(self.max_degrees, self.current_angle))
            print(f'{self.name} move to {self.current_angle} degrees')
            time.sleep(step_duration)

    def set_start_angle(self, angle):
        self.current_angle = angle

    def stabil(self):
        self.servo.angle = self.current_angle

    def home(self):
        self.move_slowly(self.home_position, duration=1)


class Tongs(ServoController):

    def __init__(self, servo_motor, home_position, steps_slow=150, steps_fast=50, max_degrees=130, min_degrees=30, name="tongs"):
        super().__init__(servo_motor, home_position, steps_slow, steps_fast, max_degrees, name)
        self.min_degrees = min_degrees

    def active(self, procent, duration=1):
        steps = self.steps_slow
        step_duration = duration / steps
        angle_step = ((procent + 30) - self.current_angle) / steps

        for _ in range(steps):
            self.current_angle += angle_step
            print(f'{self.name} degrees ${self.current_angle}')
            self.servo.angle = max(self.min_degrees, min(self.max_degrees, self.current_angle))
            time.sleep(step_duration)


def main():
    from adafruit_motor import servo
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    servo0_channel = servo.Servo(pca.channels[0], actuation_range=270, min_pulse=500, max_pulse=2500)
    servo1_channel = servo.Servo(pca.channels[1])
    servo2_channel = servo.Servo(pca.channels[2])
    servo3_channel = servo.Servo(pca.channels[13])
    servo4_channel = servo.Servo(pca.channels[14])
    servo5_channel = servo.Servo(pca.channels[15])

    all_servos = [servo0_channel, servo1_channel, servo2_channel, servo3_channel, servo4_channel, servo5_channel]

    servo_5_start_stop_position = 30
    servo_4_start_stop_position = 110
    servo_3_start_stop_position = 0
    servo_2_start_stop_position = 0
    servo_1_start_stop_position = 85
    servo_0_start_stop_position = 135

    try:
        servo0 = ServoController(servo0_channel, max_degrees=270, home_position=servo_0_start_stop_position, name="servo0")
        servo0.set_start_angle(servo_0_start_stop_position)

        servo1 = ServoController(servo1_channel, name="servo1", home_position=servo_1_start_stop_position,)
        servo1.set_start_angle(servo_1_start_stop_position)
        servo1.stabil()

        servo2 = ServoController(servo2_channel, name="servo2", home_position=servo_2_start_stop_position,)
        servo2.set_start_angle(servo_2_start_stop_position)
        servo2.stabil()

        servo3 = ServoController(servo3_channel, name="servo3", home_position=servo_3_start_stop_position,)
        servo3.set_start_angle(servo_3_start_stop_position)
        servo3.stabil()

        servo4 = ServoController(servo4_channel, name="servo4", home_position=servo_4_start_stop_position,)
        servo4.set_start_angle(servo_4_start_stop_position)

        tongs = Tongs(servo5_channel, home_position=servo_5_start_stop_position)
        tongs.set_start_angle(servo_5_start_stop_position)

        # Start - Top position
        def position_to_go():
            servo1.move_slowly(120, duration=1)
            servo2.move_slowly(50, duration=1)
            servo3.move_slowly(40, duration=1)

        position_to_go()
        # Main scripts
        servo0.move_slowly(180, duration=1)
        servo1.move_slowly(85, duration=1)
        servo2.move_slowly(20, duration=1)
        servo3.move_slowly(0, duration=1)
        tongs.active(80, duration=1)
        position_to_go()
        servo0.move_slowly(80, duration=1)
        servo1.move_slowly(85, duration=1)
        servo2.move_slowly(20, duration=1)
        servo3.move_slowly(0, duration=1)
        tongs.active(0)
        position_to_go()


        # Home
        servo0.home()
        tongs.home()
        servo1.home()
        servo2.home()
        servo3.home()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        for servo in all_servos:
            servo.angle = None
        pca.deinit()
        print("Driver PCA9685 off.")


if __name__ == "__main__":
    main()
