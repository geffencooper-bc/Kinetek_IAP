from __future__ import print_function
import can 
bus = can.interface.Bus(bustype='socketcan', channel='can0')
#vbus = can.interface.Bus(bustype='socketcan', channel='vcan0')
# while True:
#     print(bus.recv(timeout=1000))
a = 128698351616
d = a.to_bytes(5,"big")
msg = can.Message(arbitration_id=0x001,
                  data=d,
                  is_extended_id=False)
print(msg)

# try:
#     bus.send(msg)
#     print("Message sent on {}".format(bus.channel_info))   
#     msg = bus.recv(timeout=1000)
#     print(msg)
#     msg = bus.recv(timeout=1000)
#     print(msg)
#     msg = bus.recv(timeout=1000)
#     print(msg)
#     msg = bus.recv(timeout=1000)
#     print(msg)
#     # while msg.arbitration_id != 0x60:
#     #     msg = bus.recv(timeout=1000)
#     #     print(msg)
#     # data = ""
#     # for byte in msg.data:
#     #     data += hex(byte)[2:].zfill(2).upper() + " "
#     # print(msg.arbitration_id)
#     # print(data[:-1]) 
    
# except can.CanError:
#     print("Message NOT sent")
