# class to automate iap process like get code size, get start address, send hex file
from HexUtility import *
from KinetekCodes import *
import time
class IAPUtil:
    def __init__(self, is_virtual=False):
        self.code_size_bytes = 0   # integer form    ex: 92208
        self.page_check_sums = []  # list of hex strings ex: ['01 64 3C', '01 8F 75' ...]
        self.total_checksum = 0    #
        self.start_address = 0
        self.is_virtual = is_virtual
        self.in_iap_mode = False

    def load_hex_file(self, file_path):
        # get fw data from hex file
        self.hexUtil = HexUtility()
        self.hexUtil.open_file(file_path)
        self.data_size_bytes = self.hexUtil.get_file_data_size()
        self.page_check_sums = self.hexUtil.get_page_checksums()
        self.total_checksum = self.hexUtil.get_total_checksum()
        self.total_checksum_reverse = reverse_bytes(self.total_checksum)
        self.start_address = self.hexUtil.get_start_address()
        self.last_data_line_size = self.hexUtil.get_last_data_line_size()

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

        self.SEND_EOF_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("END_OF_HEX_FILE_PREFIX") \
                                                                                                        + self.last_data_line_size \
                                                                                                        + get_kinetek_data_code("END_OF_HEX_FILE_SUFFIX")))             
        self.SEND_TOTAL_CHECKSUM_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                    get_kinetek_data_code("TOTAL_CHECKSUM_PREFIX") \
                                                                                                    + reverse_bytes(self.total_checksum_reverse) \
                                                                                                    + get_kinetek_data_code("TOTAL_CHECKSUM_SUFFIX")
                                                                                                    ))
        print(self.last_data_line_size)                                                                                  
        

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
        print("\n")
        print("\t\t\t\t\t=============================================")
        print("\t\t\t\t\t=========== IAP UTILITY TO STRING ===========")
        print("\t\t\t\t\t=============================================\n\n\n\n\n\n\n")
    
    def init_can(self, channel_name):
        # need to add modprobe, ip set up stuff for ifconfig
        # maybe add a test message to send to see if works
        if self.is_virtual:
            self.bus = can.interface.Bus(bustype='socketcan', channel=channel_name)
        else:
            self.bus = can.interface.Bus(bustype='socketcan', channel=channel_name)

    def put_in_IAP_mode(self):
        self.bus.send(self.ENTER_IAP_MODE_REQUEST)
        print("Message sent on {}".format(self.bus.channel_info))   
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        enter_iap_mode_resp_count = 0 # wait till get two iap_mode responses to confirm in iap mode
        
        # repeatedly send request until enter iap mode, if receive a heartbeat then out of boot up mode and can't do forced download
        while enter_iap_mode_resp_count < 2:
            if decode_socketcan_packet(resp) != ENTER_IAP_MODE_RESPONSE: # if don't get desired response, send again
                self.bus.send(self.ENTER_IAP_MODE_REQUEST) 
                print("SENT:\t", self.ENTER_IAP_MODE_REQUEST)  
                resp = self.bus.recv(timeout=1000)
                #print(decode_socketcan_packet(resp))
                print("RECEIVED:\t", resp)
                if resp.arbitration_id == 0x80: # if the response if a heartbeat then break because left boot up mode
                     print("=========HEART BEAT DETECTED, DIDNT ENTER")
                     return False
            else: # if receive a desired response then increment the count
                enter_iap_mode_resp_count += 1
        # print("RECEIVED:\t", resp)
        # resp = self.bus.recv(timeout=1000)
        # print("RECEIVED:\t", resp)
        # resp = self.bus.recv(timeout=1000)
        # print("RECEIVED:\t", resp)
        # resp = self.bus.recv(timeout=1000)
        # print("RECEIVED:\t", resp)
        # resp = self.bus.recv(timeout=1000)
        self.in_iap_mode = True
        return True
        #print("entered iap_mode")

    def check_if_in_iap_mode(self): # if sent fw rev req it becomes 060 | 81 00 00 00 00 00 00 00
        timeout_count = 0 # if receive 20 messages with <2 iap_mode signifiers, not in IAP mode
        enter_iap_mode_resp_count = 0
        while enter_iap_mode_resp_count < 2:
            resp = self.bus.recv(timeout=1000)
            if timeout_count > 20:
                return False
            if decode_socketcan_packet(resp) != ENTER_IAP_MODE_RESPONSE:   
                resp = self.bus.recv(timeout=1000)
                timeout_count += 1
            else:
                enter_iap_mode_resp_count += 1
        return True
    
    # if expected response is received within the timeout thresh, then return True, otherwise false
    # request should be in socket_can form, expected_response should be string from lookup table
    def send_request(self, request, expected_response, timeout_count):
        self.bus.send(request)  
        print("SENT:\t", request)
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        count = 0
        while lookup(decode_socketcan_packet(resp), IAP_data_lookup) != expected_response:
            resp = self.bus.recv(timeout=1000)
            print("RECEIVED:\t", resp) 
            count += 1
            if count > timeout_count:
                return False
        return True

    # if you want to send a request multiple times, with each request having a timeout causing the next attempt to send
    def send_request_repeated(self, request, expected_response, time_out_count, max_tries, timeout_message):
        num_tries = 0
        request_status = self.send_request(request, expected_response, time_out_count)
        while request_status == False:
            request_status = self.send_request(request, expected_response, time_out_count)
            num_tries +=1
            if num_tries > max_tries:
                return (False, timeout_message) 

    def wait_for_message(self, expected_message, time_out_count, time_out_message):
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        count = 0
        while lookup(decode_socketcan_packet(resp), IAP_data_lookup) != expected_message:
            resp = self.bus.recv(timeout=1000)
            print("RECEIVED:\t", resp) 
            count += 1
            if count > time_out_count:
                return (False, time_out_message)
        #return True

    def send_init_packets(self):
        print("sending init packets")
        # make sure in iap mode first
        if self.in_iap_mode == True:
            # request fw revision
            if self.send_request(self.FW_REVISION_REQUEST, "FW_REVISION_REQUEST_RESPONSE", 20) == False:
                return "CONTROLLER WONT RESPOND TO FW REVISION REQUEST"
            # request to send bytes
            if self.send_request(self.SEND_BYTES_REQUEST, "SEND_BYTES_RESPONSE", 20) == False:
                return "CONTROLLER WONT RECEIVE BYTES"
            # request to send start address
            if self.send_request(self.SEND_START_ADDRESS_REQUEST, "SEND_START_ADDRESS_RESPONSE", 20) == False:
                return "CONTROLLER WONT RECEIVE START ADDRESS"
            # request to send checksum data
            if self.send_request(self.SEND_CHECKSUM_DATA_REQUEST, "SEND_CHECKSUM_DATA_RESPONSE", 20) == False:
                return "CONTROLLER WONT RECEIVE CHECKSUM DATA"
            # request to send start address
            if self.send_request(self.SEND_DATA_SIZE_REQUEST, "SEND_DATA_SIZE_RESPONSE", 20) == False:
                return "CONTROLLER WONT RECEIVE DATA SIZE"
            return "SUCCESS"
        return "NOT IN IAP"
    
    def upload_image(self):
        print("sending hex file...")
        self.page_count = 0
        self.packet_count = 0
        self.current_packet = [] # store in case need to retry
        write_ids = [0x04F, 0x050, 0x051, 0x052]     
        write_ids_retry = [0x053, 0x054, 0x055, 0x056]
        self.num_bytes_uploaded = 0
        
        while True:
            status = self.send_hex_packet(write_ids)
            while status == True: # keep sending hex packets until status false or none
                self.packet_count += 1
                if self.packet_count % 32 == 0: # page_cs packet needs to be made while running unless want to make all during load
                    page_cs = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                        get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                                        + self.page_check_sums[self.page_count]
                                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                                        + format_int_to_code(self.page_count+1, 1) \
                                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                                        ))
                    # need to wait for 06 pointer thing with page checksum
                    
                    resp = self.wait_for_message("SELF_CALCULATED_PAGE_CHECKSUM", 20, "NO SELF CALCULATED PAGE CHECKSUM") 
                    if resp != None and resp[0] == False:
                        return resp[1]
                    resp = self.send_request_repeated(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10, 2, "PAGE_CHECKSUM_TIMEOUT")
                    if resp != None and resp[0] == False:
                        return resp[1]
                    self.page_count += 1
                status = self.send_hex_packet(write_ids)
            if status == None: # reached end of file
                #self.page_count +=1 # (degenarate packet at the end)
                page_cs = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                    get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                                    + self.page_check_sums[self.page_count] \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                                    + format_int_to_code(self.page_count+1, 1) \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                                    ))
                resp = self.send_request_repeated(self.SEND_EOF_REQUEST, "END_OF_HEX_FILE_RESPONSE", 10, 2, "END_OF_HEX_FILE_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                
                resp = self.wait_for_message("SELF_CALCULATED_PAGE_CHECKSUM", 20, "NO SELF CALCULATED PAGE CHECKSUM") 
                if resp != None and resp[0] == False:
                    return resp[1]
                resp = self.send_request_repeated(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10, 2, "PAGE_CHECKSUM_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                resp = self.send_request_repeated(self.SEND_TOTAL_CHECKSUM_REQUEST, "CALCULATE_TOTAL_CHECKSUM_RESPONSE", 10, 2, "TOTAL_CHECKSUM_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                return (True, "EOF")
            if status == False: # retry
                status = self.send_hex_packet(write_ids_retry, True)
                if status == False:
                    return (False, "32_BYTE_RESPONSE_TIMEOUT")
                self.packet_count += 1
                continue
            
            

    def send_hex_packet(self,write_ids, is_retry=False): #32 bytes of data
        if is_retry == True:
            count = 0
            while True:
                hex_frame = make_socketcan_packet(write_ids[count], self.current_packet[count])
                if count == 3:
                    if self.send_request(hex_frame, "RECEIVED_32__BYTES", 40) == False: # if no confirmation, return false
                        return False
                    #self.num_bytes_uploaded += len(self.current_packet)
                    self.current_packet.clear() # if receive confirmation can clear and return true
                    return True

                else:
                    self.bus.send(hex_frame) 
                    #self.num_bytes_uploaded += len(self.current_packet[count])
                    print("SENT:\t",hex_frame)
                count += 1
        i = 0
        while True:
            if self.num_bytes_uploaded == self.data_size_bytes:
                return None
            data = self.hexUtil.get_next_data_8() # get the next 8 data bytes from the hex file
            self.current_packet.append(data) # stores these in case need to retry
            if data == -1: # means eof so break loop
                self.upload_done = True
                return None
            
            hex_frame = make_socketcan_packet(write_ids[i],data) # make a socket_can packet from hex data
            if i == 3: # if this is the fourth packet, wait for 32 bytes confirmation from Kinetek
                if self.send_request(hex_frame, "RECEIVED_32__BYTES", 40) == False: # if no confirmation, return false
                    return False
                print(self.current_packet)
                for chunk in self.current_packet:
                    self.num_bytes_uploaded += len(chunk)
                self.current_packet.clear() # if receive confirmation can clear and return true
                print(self.num_bytes_uploaded)
                return True

            else: # if first three packets then send normally
                self.bus.send(hex_frame) 
                #self.num_bytes_uploaded += len(data)
                print("SENT:\t",hex_frame)
            #print(self.num_bytes_uploaded)
            i += 1
            if i == len(write_ids):
                i = 0


def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3) # form: "060"
    data = ""
    for byte in frame.data:
        data += hex(byte)[2:].zfill(2).upper() + " " # form: "00 00 00 00 00 00 00 00"
    return str(can_id + " | " + data[:-1])

# ut = IAPUtil()
# ut.load_hex_file("2.28_copy.hex")
# ut.to_string()

# ut.init_can()
# ut.put_in_IAP_mode()

# if ut.put_in_IAP_mode() == True:
#     print("sending packets")
#     time.sleep(3)
#     ut.send_init_packets()
#print(ut.send_init_packets())
#ut.upload_image()