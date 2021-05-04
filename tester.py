from datetime import datetime
from time import sleep


while True:
    now = datetime.now().time()
    print(f'Min: {now.second}')
    sleep(1)
