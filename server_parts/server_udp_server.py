import json
import socket
import time

import dronekit
from dronekit import connect
import dronekit_sitl
import psutil
import GPUtil

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode

print("Start simulator (SITL)")

localIP = "192.168.0.143"
localPort = 20002
bufferSize = 1024

msgFromServer = 'alive'

bytesToSend = str.encode(msgFromServer)
# vehicle = connect(connection_string, wait_ready=True)

# Create a datagram

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print("started a server " + localIP + " "+str(localPort))

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

    controls_dict :dict = json.loads(message_from_client_str)
    if controls_dict.__contains__("axisLZ"):
        controls_dict.get("s_dict")

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
    bytesToSend = json.dumps(drone_stats_msg).encode('utf-8')

    # latitude = vehicle.location.global_relative_frame.lat
    # longitude = vehicle.location.global_relative_frame.lon
    # print(latitude)
    # print(longitude)
    # map_dat = dict(latitude="", longitude=vehicle.location.global_relative_frame.lon)
    # print(map_dat)

    time.sleep(1)

    client_address = bytesAddressPair[1]

    # clientMsg = "Message from Client:{}".format(message)
    # clientIP = "Client IP Address:{}".format(address)

    # print(clientMsg)
    # print(clientIP)

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, client_address)
