from flask import Flask, render_template, Response
import cv2
# from picamera import PiCamera
from time import sleep

app = Flask(__name__)
camera = cv2.VideoCapture(0)

"""
def generate_frames():
    while True:

        ## read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
"""


def get_picture():
    camera = PiCamera()
    camera.resolution = (640, 360)
    camera.capture('picture.jpg')
    camera.stop_preview()


@app.route('/')
def index():
    return render_template('index.html')


"""
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
"""

if __name__ == "__main__":
    try:

        app.run(debug=True, host='0.0.0.0', port=5000)
        get_picture()
    except KeyboardInterrupt:
        camera.release()
        print('KeyboardInterrupt exception is caught')
