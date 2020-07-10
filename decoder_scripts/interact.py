import can
import os

def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3) # form: "060"
    data = ""
    for byte in frame.data:
        data += hex(byte)[2:].zfill(2).upper() + " " # form: "00 00 00 00 00 00 00 00"
    return str(can_id + " | " + data[:-1])

vbus = can.interface.Bus(bustype='socketcan', channel='vcan0')
ping_msg = can.Message(arbitration_id=0x111,
                    data=[0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11],
                    is_extended_id=False)

#os.system('python3 simulator_runner.py')

while True:
    vbus.send(ping_msg)
    resp = vbus.recv(timeout=1000)
    print(resp)