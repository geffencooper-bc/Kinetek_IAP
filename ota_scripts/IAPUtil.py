# class to automate iap process like get code size, get start address, send hex file
from HexUtility import *
#from KinetekCodes import *

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

ut = IAPUtil()
ut.load_hex_file("2.28_copy.hex")
ut.to_string()