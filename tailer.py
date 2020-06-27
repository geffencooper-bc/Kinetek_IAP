# code from stack overflow to do "tail -f" in python

import time
import subprocess
import select

f = subprocess.Popen(['tail','-F','/home/geffen.cooper/vm_shared/can_logs/output.csv'],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

while True:
    if p.poll(1):
        print f.stdout.readline()