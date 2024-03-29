import socket, select, queue
import time

import GPUtil
import imutils
from flask import Flask, jsonify, Response, render_template
from celery import Celery
import psutil


import cv2
from imutils.video import VideoStream

from video_utils.get_available_cams import get_available_camera_port


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


vs = VideoStream(src=get_available_camera_port()).start()

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)



def generate_frames():
        while True:

            ## read the camera frame
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # gray = cv2.GaussianBlur(gray, (7, 7), 0)

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpeg", frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')



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

    vehicle = connect( wait_ready=True)

    # Create a datagram socket

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip

    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    # Listen for incoming datagrams

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message_from_client = bytesAddressPair[0]

        print("message_from_client")

        message_from_client_str = message_from_client.decode("utf-8")

        print(message_from_client_str)

        controls_dict: dict = json.loads(message_from_client_str)

        if controls_dict.__contains__("axisLZ"):
            controls_dict.get("")


        print(type(controls_dict))

        gpus = GPUtil.getGPUs()
        list_gpus = []
        for gpu in gpus:
            # get the GPU id
            gpu_id = gpu.id
            # name of GPU
            gpu_name = gpu.name
            # get % percentage of GPU usage of that GPU
            gpu_load = f"{gpu.load * 100}%"
            # get free memory in MB format
            gpu_free_memory = f"{gpu.memoryFree}MB"
            # get used memory
            gpu_used_memory = f"{gpu.memoryUsed}MB"
            # get total memory
            gpu_total_memory = f"{gpu.memoryTotal}MB"
            # get GPU temperature in Celsius
            gpu_temperature = f"{gpu.temperature} °C"
            gpu_uuid = gpu.uuid
            list_gpus.append((
                gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
                gpu_total_memory, gpu_temperature, gpu_uuid
            ))
        svmem = psutil.virtual_memory()
        cpufreq = psutil.cpu_freq()
        drone_stats_msg = {"cpu_core_phy": psutil.cpu_count(logical=False),
                           "cpu_core_total": psutil.cpu_count(logical=True),
                           # "cpu_freq_max": cpufreq.max,
                           # "cpu_freq_min": cpufreq.min,
                           "cpu_freq_curr": cpufreq.current,
                           "cpu_freq_perc_simple": psutil.cpu_percent(),
                           "ram_used": svmem.percent,
                           "gpu_name": gpu.name,
                           "gpu_used": gpu.load * 100,
                           "gpu_temp": gpu.temperature,
                           "latitude": 48.7943178,
                           "longitude": 9.1902554,
                           }


        print(drone_stats_msg)
        client_address = bytesAddressPair[1]

        bytesToSend = json.dumps(drone_stats_msg).encode('utf-8')

        UDPServerSocket.sendto(bytesToSend, client_address)


@app.route("/")
def test_home():
    listen_to_udp.delay()
    d = {"status": "alive"}
    print("server is running")

    return jsonify(d)




if __name__ == "__main__":
    try:
        # run install.py to install dependencies and create the database
        app.run(host="0.0.0.0", port=5000, debug=False)
    except:
        vs.stop()
        # camera.release()
        print('KeyboardInterrupt exception is caught')




