# class to automate iap process like get code size, get start address, send hex file
from HexUtility import *
from KinetekCodes import *
import time
class IAPUtil:
    def __init__(self):
        self.code_size_bytes = 0
        self.page_check_sums = []
        self.total_checksum = 0
        self.code_start_address = 0

    def load_hex_file(self, file_path):
        self.hexUtil = HexUtility()
        self.hexUtil.open_file(file_path)
        self.code_size_bytes = self.hexUtil.get_file_data_size()
        self.page_check_sums = self.hexUtil.get_page_checksums()
        self.total_checksum = self.hexUtil.get_total_checksum()
        self.code_start_address = self.hexUtil.get_start_address()

    def to_string(self):
        print("CODE SIZE:\t", self.code_size_bytes, "bytes")
        print("TOTAL CHECKSUM:\t", self.total_checksum)
        print("START ADDRESS:\t", self.code_start_address)
        print("PAGE CHECKSUMS:\t", self.page_check_sums)
    
    def init_can(self):
        # implement later
        self.bus = can.interface.Bus(bustype='socketcan', channel='can0')

    def put_in_IAP_mode(self):
        frame = ENTER_IAP_MODE_REQUEST
        self.bus.send(frame)
        start_time = frame.timestamp
        print("Message sent on {}".format(self.bus.channel_info))   
        resp = self.bus.recv(timeout=1000)
        curr_time = resp.timestamp
        enter_iap_mode_resp_count = 0
        while enter_iap_mode_resp_count < 2:
            if decode_socketcan_packet(resp) != ENTER_IAP_MODE_RESPONSE:
                #frame = ENTER_IAP_MODE_REQUEST
                self.bus.send(frame)
                #print("Message sent on {}".format(self.bus.channel_info)) 
                #print("SENT:\t", frame)
                #print("Message sent on {}".format(self.bus.channel_info))   
                resp = self.bus.recv(timeout=1000)
                print("RECEIVED:\t", resp)
                #curr_time = resp.timestamp
                if resp.arbitration_id == 0x80:
                     print("HEART BEAT DETECTED, DIDNT ENTER")
                     break
            else:
                enter_iap_mode_resp_count += 1
        print("entered iap_mode")
        # count = 0
        # while count < 121:
        #     frame = ENTER_IAP_MODE_REQUEST
        #     self.bus.send(frame)
        #     count += 1
        
        # count = 0
        # while count < 1000:
        #     resp = self.bus.recv(timeout=1000)
        #     print(resp)
        #     count += 1


# class SimpleFrame:
#     # last_time_stamp = 0
#     # curr_time_stamp = 0 # these are static variables shared accross all instances
#     # time_stamp_delta = 0 # used to detect a timeout
#     def __init__(self, time_stamp, can_id, data):
#         self.time_stamp = time_stamp
#         self.can_id = can_id
#         self.data = data
#         # update these
#         # self.last_time_stamp = self.curr_time_stamp
#         # self.curr_time_stamp = time_stamp

def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3) # form: "060"
    data = ""
    for byte in frame.data:
        data += hex(byte)[2:].zfill(2).upper() + " " # form: "00 00 00 00 00 00 00 00"
    #simple_frame = SimpleFrame(frame.timestamp, can_id, data[:-1])
    return str(can_id + " | " + data)

ut = IAPUtil()
ut.load_hex_file("2.28_copy.hex")
ut.to_string()

ut.init_can()
ut.put_in_IAP_mode()