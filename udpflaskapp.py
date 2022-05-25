import socket, select, queue

from flask import Flask, jsonify, Response, render_template
from celery import Celery
import psutil


import cv2


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)

camera = cv2.VideoCapture(0)


def generate_frames():
    while True:

        ## read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            ret, buffer = cv2.imencode('.jpg', frame,encode_param)
            frame = buffer.tobytes()
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream')
def index():
    return render_template('index.html')


@celery.task(name="udp_work_cel")
def listen_to_udp():
    """
    This code was taken from
    https://stackoverflow.com/questions/9969259/python-raw-socket-listening-for-udp-packets-only-half-of-the-packets-received


    """
    import json
    import socket
    # SITL not working on Rpi
    # import dronekit_sitl

    # sitl = dronekit_sitl.start_default()
    # connection_string = sitl.connection_string()

    # Import DroneKit-Python
    from dronekit import connect, VehicleMode

    print("Start simulator (SITL)")

    localIP = "0.0.0.0"
    localPort = 20002
    bufferSize = 1024

    # vehicle = connect(connection_string, wait_ready=True)

    # Create a datagram socket

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip

    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    # Listen for incoming datagrams

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        latitude = 48.781391
        longitude = 9.180812

        # latitude = vehicle.location.global_relative_frame.lat
        # longitude = vehicle.location.global_relative_frame.lon
        print(latitude)
        print(longitude)
        map_dat = dict(latitude=latitude, longitude=longitude)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP = "Client IP Address:{}".format(address)

        # print(clientMsg)
        # print(clientIP)
        msgFromServer = 'Empty'

        bytesToSend: bytes = str.encode(json.dumps(map_dat))

        # Sending a reply to client

        UDPServerSocket.sendto(bytesToSend, address)
    # print("task is running")

    # udp_socket: socket.socket
    ##udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_socket.bind(('0.0.0.0', 1337))
    #  s2 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    #  s2.bind(('0.0.0.0', 1337))
    # print("task is running")
    # while True:
    #  r, w, x = select.select([udp_socket], [], [])
    #   for i in r:
    #     print((i, i.recvfrom(131072)))


@app.route("/")
def test_home():
    listen_to_udp.delay()
    d = {"status": "alive"}
    print("server is running")

    return jsonify(d)


if __name__ == "__main__":
    # run install.py to install dependencies and create the database
    app.run(host="0.0.0.0", port=5000, debug=False)
