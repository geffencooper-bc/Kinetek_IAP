# class to automate iap process like get code size, get start address, send hex file
from HexUtility import *
from KinetekCodes import *
import time
class IAPUtil:
    def __init__(self):
        self.code_size_bytes = 0   # integer form    ex: 92208
        self.page_check_sums = []  # list of hex strings ex: ['01 64 3C', '01 8F 75' ...]
        self.total_checksum = 0    #
        self.start_address = 0

    def load_hex_file(self, file_path):
        # get fw data from hex file
        self.hexUtil = HexUtility()
        self.hexUtil.open_file(file_path)
        self.data_size_bytes = self.hexUtil.get_file_data_size()
        self.page_check_sums = self.hexUtil.get_page_checksums()
        self.total_checksum = self.hexUtil.get_total_checksum()
        self.start_address = self.hexUtil.get_start_address()

        # make socket_can commands
        self.FW_REVISION_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("FW_REVISION_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("DEFAULT")))
        self.ENTER_IAP_MODE_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("ENTER_IAP_MODE")))
        self.SEND_BYTES_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("SEND_BYTES")))
        self.SEND_START_ADDRESS_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                        get_kinetek_data_code("CODE_START_ADDRESS_PREFIX") \
                                                                                                        + insert_spaces(self.start_address, 2)
                                                                                                        + get_kinetek_data_code("CODE_START_ADDRESS_SUFFIX")
                                                                                                        ))
        self.SEND_CHECKSUM_DATA_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                        get_kinetek_data_code("SEND_CHECKSUM_PREFIX") \
                                                                                                        + self.total_checksum
                                                                                                        + get_kinetek_data_code("SEND_CHECKSUM_SUFFIX")
                                                                                                        ))
        self.SEND_DATA_SIZE_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                        get_kinetek_data_code("SEND_DATA_SIZE_PREFIX") \
                                                                                                        + format_int_to_code(self.data_size_bytes, 4)
                                                                                                        + get_kinetek_data_code("SEND_DATA_SIZE_SUFFIX")
                                                                                                        ))                                                                                                  
        

    def to_string(self):
        print("\n")
        print("\t\t\t\t\t=============================================")
        print("\t\t\t\t\t=========== IAP UTILITY TO STRING ===========")
        print("\t\t\t\t\t=============================================\n\n")
        print("HEX FILE DATA SIZE:\t\t", self.data_size_bytes, "bytes")
        print("HEX FILE DATA TOTAL CHECKSUM:\t", self.total_checksum)
        print("START ADDRESS:\t\t\t", self.start_address)
        print("PAGE CHECKSUMS:\t", self.page_check_sums)
        print("\n\n==== INIT COMMANDS====\n\nFW_REVISION_REQUEST:\t\t", self.FW_REVISION_REQUEST)
        print("\nENTER_IAP_MODE_REQUEST:\t\t", self.ENTER_IAP_MODE_REQUEST)
        print("\nSEND_BYTES_REQUEST:\t\t", self.SEND_BYTES_REQUEST)
        print("\nSEND_START_ADDRESS_REQUEST:\t", self.SEND_START_ADDRESS_REQUEST)
        print("\nSEND_CHECKSUM_DATA_REQUEST:\t", self.SEND_CHECKSUM_DATA_REQUEST)
        print("\nSEND_DATA_SIZE_REQUEST:\t\t", self.SEND_DATA_SIZE_REQUEST)
    
    def init_can(self):
        # implement later
        self.bus = can.interface.Bus(bustype='socketcan', channel='can0')

    def put_in_IAP_mode(self):
        self.bus.send(ENTER_IAP_MODE_REQUEST)
        start_time = frame.timestamp
        print("Message sent on {}".format(self.bus.channel_info))   
        resp = self.bus.recv(timeout=1000)
        #curr_time = resp.timestamp
        enter_iap_mode_resp_count = 0
        while enter_iap_mode_resp_count < 2:
            if decode_socketcan_packet(resp) != ENTER_IAP_MODE_RESPONSE:
                self.bus.send(ENTER_IAP_MODE_REQUEST) 
                #print("SENT:\t", frame)  
                resp = self.bus.recv(timeout=1000)
                print("RECEIVED:\t", resp)
                #curr_time = resp.timestamp
                if resp.arbitration_id == 0x80:
                     print("HEART BEAT DETECTED, DIDNT ENTER")
                     break
            else:
                enter_iap_mode_resp_count += 1
        print("RECEIVED:\t", resp)
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        resp = self.bus.recv(timeout=1000)
        print("entered iap_mode")

    def check_if_in_iap_mode(self):
        timeout_count = 0 # if receive 20 messages with <2 iap_mode signifiers, not in IAP mode
        while enter_iap_mode_resp_count < 2:
            resp = self.bus.recv(timeout=1000)
            if count > 20:
                return False
            if decode_socketcan_packet(resp) != ENTER_IAP_MODE_RESPONSE:   
                resp = self.bus.recv(timeout=1000)
                count += 1
            else:
                enter_iap_mode_resp_count += 1
        return True
    
    # if expected response is received within the timeout thresh, then return True, otherwise false
    # request should be in socket_can form, expected_response should be string from lookup table
    def send_request(self, request, expected_response, timeout_count):
        self.bus.send(request)  
        resp = self.bus.recv(timeout=1000)
        count = 0
        while lookup(decode_socketcan_packet(resp), IAP_data_lookup) != expected_response:
            resp = self.bus.recv(timeout=1000)
            print("RECEIVED:\t", resp) 
            count += 1
            if count > timeout_count:
                return False
        return True

    def send_init_packets(self):
        # make sure in iap mode first
        if self.check_if_in_iap_mode() == True:
            # request fw revision
            if self.send_request(self.FW_REVISION_REQUEST, "FW_REVISION_REQUEST_RESPONSE", 10) == False:
                return "CONTROLLER WONT RECEIVE BYTES"
            # request to send bytes
            if self.send_request(self.SEND_BYTES_REQUEST, "SEND_BYTES_RESPONSE", 10) == False:
                return "CONTROLLER WONT RECEIVE BYTES"
            #if self.send_request()

       


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
    return str(can_id + " | " + data[:-1])

ut = IAPUtil()
ut.load_hex_file("2.28_copy.hex")
ut.to_string()

#ut.init_can()
#ut.put_in_IAP_mode()
#ut.send_init_packets()