from __future__ import print_function
import can 
bus = can.interface.Bus(bustype='socketcan', channel='can0')
msg = can.Message(arbitration_id=0x001,
                    data=[0x1D, 0xF9, 0x01, 0x00, 0x01],
                    is_extended_id=False)

try:
    bus.send(msg)
    print("Message sent on {}".format(bus.channel_info))   
    msg = bus.recv(timeout=1000)
    print(msg) 
except can.CanError:
    print("Message NOT sent")
