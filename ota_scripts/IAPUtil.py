# class to automate iap process like get code size, get start address, send hex file
from HexUtility import *
from KinetekCodes import *

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
        pass

    def put_in_IAP_mode(self):
        command = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("ENTER_IAP_MODE"))
        # while loop


class SimpleFrame:
    last_time_stamp = 0
    curr_time_stamp = 0
    time_stamp_delta = 0 # used to detect a timeout
    def __init__(self, time_stamp, can_id, data):
        self.time_stamp = time_stamp
        self.can_id = can_id
        self.data = data

def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3)
        data = ""
        for byte in frame.data:
           data += hex(byte)[2:].zfill(2).upper() + " "
        simple_frame = SimpleFrame(frame.timestamp, can_id, data[:-1])

ut = IAPUtil()
ut.load_hex_file("2.28_copy.hex")
ut.to_string()