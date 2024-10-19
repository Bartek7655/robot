# import time
# from os.path import curdir
#
# import board
# import busio
# from adafruit_motor import servo
# from adafruit_pca9685 import PCA9685
#
# # Inicjalizacja I2C i PCA9685
# i2c = busio.I2C(board.SCL, board.SDA)
# pca = PCA9685(i2c)
# pca.frequency = 50  # Częstotliwość dla serwomechanizmów (50 Hz)
#
# # Inicjalizacja serwomechanizmu
# servo0 = servo.Servo(pca.channels[0], actuation_range=270, min_pulse=500, max_pulse=2500)
# servo1 = servo.Servo(pca.channels[1])
# servo2 = servo.Servo(pca.channels[2])
# servo3 = servo.Servo(pca.channels[13])
# servo4 = servo.Servo(pca.channels[14])
# servo5 = servo.Servo(pca.channels[15])
#
# all_servos = [servo0, servo1, servo2, servo3, servo4, servo5]
#
# servo_5_start_stop_position = 30
# servo_4_start_stop_position = 110
# servo_3_start_stop_position = 0
# servo_2_start_stop_position = 0
# servo_1_start_stop_position = 85
# servo_0_start_stop_position = 135
#
#
# current_servo_0 = 0
# current_servo_1 = 0
# current_servo_2 = 0
# current_servo_3 = 0
# current_servo_4 = 0
# current_servo_5 = 0
#
# # servo_4_start_position = 90
# # servo_3_start_position = 90
# # servo_2_start_position = 20
# # servo_1_start_position = 140
#
#
# def tongs_active(start_angle, procent, duration):
#     global current_servo_5
#     steps = 100
#     step_duration = duration / steps
#     angle_step = ((procent + 30) - start_angle) / steps
#
#     current_angle = start_angle
#
#     for _ in range(steps):
#         current_angle += angle_step
#         print(f'{"tongs"} degrees', current_angle)
#         servo5.angle = max(30, min(130, current_angle))
#         time.sleep(step_duration)
#         current_servo_5 = servo5.angle
#     return current_angle
#
# def go_right(start_angle, position, duration):
#     steps = 100
#     step_duration = duration / steps
#     angle_step = (position - start_angle) / steps
#
#     current_angle = start_angle
#
#     for _ in range(steps):
#         current_angle += angle_step
#         print(f'Going right degrees', current_angle)
#         servo0.angle = max(0, min(270, current_angle))
#         time.sleep(step_duration)
#     return current_angle
#
#
# def go_left(start_angle, position, duration):
#     steps = 100
#     step_duration = duration / steps
#     angle_step = (position - start_angle) / steps
#
#     current_angle = start_angle
#
#     for _ in range(steps):
#         current_angle += angle_step
#         print(f'Going left degrees', current_angle)
#         servo0.angle = max(0, min(270, current_angle))
#         time.sleep(step_duration)
#     return current_angle
#
#
# def move_servo_slowly(string_servo, servo_active, start_angle, end_angle, duration):
#     steps = 100
#     step_duration = duration / steps
#     angle_step = (end_angle - start_angle) / steps
#
#     current_angle = start_angle
#     for _ in range(steps):
#         current_angle += angle_step
#         print(f'{string_servo} kat', current_angle)
#         servo_active.angle = max(0, min(180, current_angle))
#         # servo_active.angle = max(0, min(270, current_angle))  # Ograniczenie do zakresu 0-270 stopni
#         time.sleep(step_duration)
#     return current_angle
#
#
# def move_servo_slowly_270(string_servo, servo_active, start_angle, end_angle, duration):
#     steps = 100
#     step_duration = duration / steps
#     angle_step = (end_angle - start_angle) / steps
#
#     current_angle = start_angle
#     for _ in range(steps):
#         current_angle += angle_step
#         print(f'{string_servo} kat', current_angle)
#         servo_active.angle = max(0, min(270, current_angle))  # Ograniczenie do zakresu 0-270 stopni
#         time.sleep(step_duration)
#     return current_angle
#
#
# try:
#     servo2.angle = servo_2_start_stop_position
#     servo3.angle = servo_3_start_stop_position
#
#     servo_1_last = move_servo_slowly("servo1", servo1, servo_1_start_stop_position, 120, 2)
#     servo_2_last = move_servo_slowly("servo2", servo2, servo_2_start_stop_position, 70, 2)
#     servo_3_last = move_servo_slowly("servo3", servo3, servo_3_start_stop_position, 70, 2)
#     go_right(servo_0_start_stop_position, 270, 3)
#     go_right(servo_0_start_stop_position, 135, 3)
#     #
#     # servo_0_last = move_servo_slowly_270("servo0", servo0, servo_0_start_stop_position, 270, 3)
#     # servo_0_last = move_servo_slowly_270("servo0", servo0, servo_0_last, 135, 3)
#     #
#     # servo_1_last = move_servo_slowly("servo1", servo1, servo_1_last, servo_1_start_stop_position+10, 2)
#     # servo_2_last = move_servo_slowly("servo2", servo2, servo_2_last, servo_2_start_stop_position+15, 2)
#     # servo_3_last = move_servo_slowly("servo3", servo3, servo_3_last, servo_3_start_stop_position-25, 2)
#     # servo_1_last = move_servo_slowly("servo1", servo1, servo_1_last, servo_1_last+10, 2)
#     #
#     # #
#     # tongs_active(servo_5_start_stop_position, 100, 1)
#     #
#     # servo_1_last = move_servo_slowly("servo1", servo1, servo_1_last, 120, 2)
#     # servo_2_last = move_servo_slowly("servo2", servo2, servo_2_last, 70, 2)
#     # servo_3_last = move_servo_slowly("servo3", servo3, servo_3_last, 70, 2)
#     #
#     # servo_0_last = move_servo_slowly_270("servo0", servo0, servo_0_last, 0, 3)
#     # tongs_active(servo_5_start_stop_position, 0, 1)
#     #
#     # servo_0_last = move_servo_slowly_270("servo0", servo0, servo_0_last, 135, 3)
#     #
#     # servo_1_last = move_servo_slowly("servo1", servo1, servo_1_last, servo_1_start_stop_position, 2)
#     # servo_2_last = move_servo_slowly("servo2", servo2, servo_2_last, servo_2_start_stop_position, 2)
#     # servo_3_last = move_servo_slowly("servo3", servo3, servo_3_last, servo_3_start_stop_position, 2)
#
#     #
#     #
#
#     print('========================================stop mojego skryptu')
#
# except KeyboardInterrupt:
#     pass
#
# finally:
#     for servo in all_servos:
#         servo.angle = None
#     pca.deinit()
#     print("Sterownik PCA9685 wyłączony.")
