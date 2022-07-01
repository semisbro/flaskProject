import io

import imutils
import numpy as np
from flask import Flask, render_template, Response
import cv2
from time import sleep
import time

from PIL import Image, ImageFont, ImageDraw


app = Flask(__name__)
camera = cv2.VideoCapture(0,cv2.CAP_ANY)
camera.set(cv2.CAP_PROP_FPS,60)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))





def generate_frames():
    # used to record the time when we processed last frame
    prev_frame_time = 0

    # used to record the time at which we processed current frame
    new_frame_time = 0
    while True:

        ## read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:

            frame = imutils.resize(frame, width=500, height=500)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.dstack([frame, frame, frame])


            #encode_param = [int(cv2.IMWRITE_JPEG_OPTIMIZE), 60]
           # ret, buffer = cv2.imencode('.jpeg', frame,encode_param)

            # time when we finish processing for this frame
            new_frame_time = time.time()

            # Calculating the fps

            my_image = Image.fromarray(frame)
            d1 = ImageDraw.Draw(my_image)

            # converting the fps into integer

            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps_real = camera.get(cv2.CAP_PROP_FPS)



            fps = int(fps)

            d1.text((0, 0), "Running at :"+" "+str(fps_real)+ " FPS", fill=(255, 0, 0))
            img_byte_arr = io.BytesIO()
            my_image.save(img_byte_arr, format='JPEG')

            img_byte_arr = img_byte_arr.getvalue()




            # Use putText() method for
            # inserting text on video



            #frame = buffer.tobytes()




        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')


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
        camera.release()
        print('KeyboardInterrupt exception is caught')
