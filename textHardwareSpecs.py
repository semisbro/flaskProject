from tqdm import tqdm
from time import sleep

import psutil

with tqdm(total=100, desc='cpu%', position=1) as cpubar, tqdm(total=100, desc='ram%', position=0) as rambar:
    while True:
        rambar.n = psutil.virtual_memory().percent
        cpubar.n = psutil.cpu_percent()
        rambar.refresh()
        cpubar.refresh()

        print(psutil.virtual_memory().percent)
        print(psutil.cpu_percent())

        sleep(0.5)
