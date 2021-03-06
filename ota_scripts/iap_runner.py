import can
import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
from IAPUtil import IAPUtil

# can test if the kinetek simulator connected using a ping frame

# vbus = can.interface.Bus(bustype='socketcan', channel='vcan0')
# ping_msg = can.Message(arbitration_id=0x111,
#                     data=[0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11],
#                     is_extended_id=False)

# the IAP download utility which helps automates the process, false means use real kinetek not virtual 
ut = IAPUtil(True) 
ut.init_can("can0")

# extracts all needed iap information from hex file like checksum, size, start address. Also reads this file while hex data uploaded
ut.load_hex_file("/home/geffen.cooper/Desktop/kinetek_scripts/hex_file_copies/2.27_copy.hex")
ut.print() # print important hexfile data

# print("try to enter iap")

#ut.turn_on_print()
ut.put_in_IAP_mode(False)

ut.in_iap_mode = True
status = ut.send_init_packets()
print(status)
if status == "SUCCESS":
    print(ut.upload_image())

# while True:
#     print(ping_msg)
#     vbus.send(ping_msg)
#     resp = vbus.recv(timeout=1000)
#     print(resp)