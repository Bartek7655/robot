from flask import Flask, Response
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>Live Streaming</title>
            </head>
            <body>
                <h1>Live Stream</h1>
                <img src="/video_feed" width="640" height="480" />
            </body>
        </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)