import select
import sys
import threading
import time

import board
import busio
import cv2
import numpy as np
from adafruit_pca9685 import PCA9685
from flask import Flask, render_template, Response

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Globalne zmienne
output_frame = None
lock = threading.Lock()

# Zmienne dla detekcji niebieskiego pudełka
blue_box_detected = False
blue_box_position = None  # współrzędna x środka niebieskiego pudełka

# Dodajemy stop_event do kontrolowania zakończenia programu
stop_event = threading.Event()
# lower_blue = np.array([100, 150, 50])
# upper_blue = np.array([140, 255, 255])
# Zakres kolorów dla niebieskiego (w przestrzeni HSV)
lower_blue = np.array([12, 180, 150])
upper_blue = np.array([20, 255, 255])


# Funkcja do przechwytywania klatek z kamery i detekcji niebieskiego pudełka
def capture_frames():
    global output_frame, blue_box_detected, blue_box_position

    # Inicjalizacja kamery
    camera = cv2.VideoCapture(0)
    # Ustawienie rozdzielczości kamery
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while not stop_event.is_set():
        success, frame = camera.read()
        if not success:
            print("Nie udało się przechwycić klatki z kamery.")
            break

        # Konwersja do przestrzeni barw HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Tworzenie maski dla niebieskiego koloru
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Znajdowanie konturów w masce
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        with lock:
            if contours:
                # Znajdź największy kontur
                largest_contour = max(contours, key=cv2.contourArea)
                # Pobierz prostokąt otaczający
                x, y, w, h = cv2.boundingRect(largest_contour)
                # Oblicz środek pudełka
                blue_box_position = x + w / 2

                # Ustaw blue_box_detected na True
                blue_box_detected = True

                # Rysuj prostokąt na klatce
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            else:
                # Nie wykryto niebieskiego pudełka
                blue_box_detected = False
                blue_box_position = None

            # Kopiuj klatkę do wyświetlenia
            output_frame = frame.copy()

        time.sleep(0.03)  # Dostosuj opóźnienie w razie potrzeby

    camera.release()


# Funkcja do generowania klatek dla Flaska
def generate():
    global output_frame
    while not stop_event.is_set():
        with lock:
            if output_frame is None:
                continue
            # Kodowanie klatki do formatu JPEG
            ret, buffer = cv2.imencode('.jpg', output_frame)
            if not ret:
                continue
            frame = buffer.tobytes()

        # Wysyłanie klatki do klienta
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Trasy Flask
@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')


# Klasy sterujące serwomechanizmami
class ServoController:
    def __init__(self, servo_motor, home_position, steps_slow=50, steps_fast=50, max_degrees=180, name=''):
        self.servo = servo_motor
        self.current_angle = home_position
        self.steps_slow = steps_slow
        self.steps_fast = steps_fast
        self.max_degrees = max_degrees
        self.name = name
        self.home_position = home_position
        self.servo.angle = home_position  # Ustaw serwo na pozycję domową

    def move_slowly(self, end_angle, duration=1.0):
        steps = self.steps_slow
        step_duration = duration / steps
        angle_step = (end_angle - self.current_angle) / steps

        for _ in range(steps):
            if stop_event.is_set():
                break
            self.current_angle += angle_step
            self.servo.angle = max(0, min(self.max_degrees, self.current_angle))
            # Możesz odkomentować poniższą linię do debugowania
            # print(f'{self.name} move to {self.current_angle:.2f} degrees')
            time.sleep(step_duration)

    def set_start_angle(self, angle):
        self.current_angle = angle
        self.servo.angle = angle

    def stabil(self):
        self.servo.angle = self.current_angle

    def home(self):
        self.move_slowly(self.home_position, duration=1.0)


# Funkcja sterująca robotem
def robot_control():
    global blue_box_detected, blue_box_position

    from adafruit_motor import servo
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    # Inicjalizacja serwomechanizmów
    servo0_channel = servo.Servo(pca.channels[0], actuation_range=270, min_pulse=500, max_pulse=2500)
    servo1_channel = servo.Servo(pca.channels[1])
    servo2_channel = servo.Servo(pca.channels[2])
    servo3_channel = servo.Servo(pca.channels[13])
    # Dodatkowe serwa można dodać w razie potrzeby

    all_servos = [servo0_channel, servo1_channel, servo2_channel, servo3_channel]

    # Pozycje początkowe
    servo_0_start_stop_position = 135  # Pozycja środkowa
    servo_1_start_stop_position = 85
    servo_2_start_stop_position = 0
    servo_3_start_stop_position = 0

    try:
        # Inicjalizacja kontrolerów serw
        servo0 = ServoController(servo0_channel, home_position=servo_0_start_stop_position, max_degrees=270,
                                 name="servo0")
        servo0.set_start_angle(servo_0_start_stop_position)

        servo1 = ServoController(servo1_channel, home_position=servo_1_start_stop_position, name="servo1")
        servo1.set_start_angle(servo_1_start_stop_position)
        servo1.stabil()

        servo2 = ServoController(servo2_channel, home_position=servo_2_start_stop_position, name="servo2")
        servo2.set_start_angle(servo_2_start_stop_position)
        servo2.stabil()

        servo3 = ServoController(servo3_channel, home_position=servo_3_start_stop_position, name="servo3")
        servo3.set_start_angle(servo_3_start_stop_position)
        servo3.stabil()

        # Funkcja do podniesienia ramienia
        def position_to_go():
            servo1.move_slowly(120, duration=1.0)
            servo2.move_slowly(50, duration=1.0)
            servo3.move_slowly(40, duration=1.0)

        # Funkcja do obracania serwa 0 w trybie skanowania
        def scan_servo0():
            for angle in (range(0, 270, 40)):
                if blue_box_detected:
                    break
                servo0.move_slowly(angle, duration=2.0)
            time.sleep(0.2)

        # Podniesienie ramienia
        position_to_go()

        # Stan robota: 'scanning' lub 'following'
        state = 'scanning'

        # Parametry kontrolne
        Kp = 0.1  # Proporcjonalny współczynnik sterowania
        dead_zone = 40  # Minimalne przesunięcie do reakcji (piksele)

        # Filtrowanie pozycji pudełka (przykładowa implementacja)
        # Możesz użyć bardziej zaawansowanego filtru, jeśli potrzebujesz
        position_history = []
        history_length = 10

        while not stop_event.is_set():
            if state == 'scanning':
                scan_servo0()
                if blue_box_detected:
                    # Dodaj do historii
                    position_history.append(blue_box_position)
                    if len(position_history) > history_length:
                        position_history.pop(0)
                    # Sprawdź, czy pozycja jest stabilna
                    state = 'following'
                    print("Przechodzę do trybu śledzenia.")
                else:
                    position_history.clear()
            elif state == 'following':
                if blue_box_detected and blue_box_position is not None:
                    # Compute the position of the box relative to the image
                    frame_width = 1280  # Adjust as necessary
                    frame_center_x = frame_width / 2
                    object_center_x = blue_box_position

                    # Compute offset
                    offset_x = object_center_x - frame_center_x

                    print(f"Offset_x: {offset_x}")

                    if abs(offset_x) > dead_zone:
                        # Compute angle correction
                        angle_adjustment = Kp * (offset_x / frame_center_x) * 270  # max_servo_angle=270

                        print(f"Angle adjustment: {angle_adjustment}")

                        # Compute new servo angle
                        target_angle = servo_0_start_stop_position - angle_adjustment

                        print(f"Target angle before clamping: {target_angle}")

                        # Limit the angle to the servo range
                        target_angle = max(0, min(servo0.max_degrees, target_angle))

                        print(f"Target angle after clamping: {target_angle}")

                        # Move servo 0 to follow the blue box
                        servo0.move_slowly(target_angle, duration=1)
                        print(f"Servo moved to {target_angle:.2f} degrees (offset: {offset_x:.2f} pixels)")

                    else:
                        print('The object is near the center, no correction needed')
                    time.sleep(0.1)
            else:
                # The box disappeared, return to scanning mode
                state = 'scanning'
                position_history.clear()
                print("The box disappeared. Returning to scanning mode.")

    except Exception as e:
        print(f"An error occurred in robot_control: {e}")
    finally:
        # Czyszczenie
        for servo in all_servos:
            servo.angle = None
        pca.deinit()
        print("Driver PCA9685 off.")


# Funkcja do wykrywania naciśnięcia klawisza 'Q'
def keyboard_listener():
    print("Aby zakończyć program, naciśnij 'Q'.")
    while not stop_event.is_set():
        # Sprawdzanie dostępnych danych wejściowych bez blokowania
        if sys.stdin in select.select([sys.stdin], [], [], 1)[0]:
            user_input = sys.stdin.readline().strip()
            if user_input.lower() == 'q':
                print("Naciśnięto 'Q'. Kończenie programu.")
                stop_event.set()
                break
            else:
                print(f"Naciśnięto '{user_input}'. Aby zakończyć program, naciśnij 'Q'.")


# Główna funkcja
def main():
    try:
        # Uruchomienie wątków
        t1 = threading.Thread(target=capture_frames)
        t2 = threading.Thread(target=robot_control)
        t3 = threading.Thread(target=keyboard_listener)

        t1.start()
        t2.start()
        t3.start()

        # Uruchomienie aplikacji Flask
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("Program przerwany przez użytkownika.")
        stop_event.set()
    finally:
        # Ustawienie flagi zatrzymania dla wszystkich wątków
        stop_event.set()
        # Oczekiwanie na zakończenie wątków
        t1.join()
        t2.join()
        t3.join()
        print("Program zakończony.")


if __name__ == '__main__':
    main()
