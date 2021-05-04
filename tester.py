from datetime import datetime
from time import sleep


m: dict[str] = {}
m['a'] = 1

if m.__contains__('b'):
    m['b'] += 1
else:
    m['b'] = 1

print(m)
