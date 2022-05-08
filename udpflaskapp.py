import socket, select, queue

from flask import Flask, jsonify
from celery import Celery


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


@celery.task(name="udp_work_cel")
def listen_to_udp():
    """
    This code was taken from
    https://stackoverflow.com/questions/9969259/python-raw-socket-listening-for-udp-packets-only-half-of-the-packets-received


    """
    import json
    import socket
    import dronekit_sitl

    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

    #Import DroneKit-Python
    from dronekit import connect, VehicleMode

    print("Start simulator (SITL)")

    localIP = "0.0.0.0"
    localPort = 9000
    bufferSize = 1024

    vehicle = connect(connection_string, wait_ready=True)

    # Create a datagram socket

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip

    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    # Listen for incoming datagrams

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        # latitude = 48.777111
        #longitude = 9.180770

        latitude = vehicle.location.global_relative_frame.lat
        longitude = vehicle.location.global_relative_frame.lon
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
    app.run(host="0.0.0.0", port=5000, debug=True)
