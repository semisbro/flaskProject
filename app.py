import io

import imutils
import numpy as np
from flask import Flask, render_template, Response
import cv2
from time import sleep
import time

from PIL import Image, ImageFont, ImageDraw
from imutils.video import VideoStream

app = Flask(__name__)
vs = VideoStream(src=0).start()







def generate_frames():
    # used to record the time when we processed last frame
    prev_frame_time = 0

    # used to record the time at which we processed current frame
    new_frame_time = 0
    while True:

        ## read the camera frame
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpeg", frame)
        # ensure the frame was successfully encoded
        if not flag:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')








@app.route('/')
def index():

    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    try:

        app.run(debug=False, host='0.0.0.0', port=5000)

    except KeyboardInterrupt:
        vs.stop()
        #camera.release()
        print('KeyboardInterrupt exception is caught')
