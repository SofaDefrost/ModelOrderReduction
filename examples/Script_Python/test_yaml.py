import os,time,sys
import yaml

from loadBar import update_progress

for i in range(101):
    time.sleep(0.1)
    update_progress(i/100.0)

