import datetime
import time

a = datetime.datetime.now() + datetime.timedelta(seconds=5)
c = datetime.datetime.now()
# b = datetime.time(1970, 1, 1)
d = a - c
if d == datetime.timedelta(seconds=5):
    print("dale")
else:
    print("F")

print(d)