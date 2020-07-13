#!/usr/bin/env python3



from HexUtility import *     # all hex file helper functions
from KinetekCodes import *   # config file with all kinetek commands
import time

# class to automate iap process by reading and uploading data from a hex file

class IAPUtil:
    def __init__(self, is_virtual=False):
        # all bytes lists are in big endian form
        self.start_address = []       # ex: [0x08, 0x00, 0x80, 0x00] --> 08008000
        self.data_size_bytes = []     # ex: [0x00, 0x01, 0x67, 0x24] --> 92208 bytes
        self.page_check_sums = []     # ex: [[0x01, 0x64, 0x3C], [0x01, 0x8F, 0x75] ...] --> [0x01643C, 0x018F75, ...]
        self.total_checksum = []      # ex: [0x00, 0x086, 0xC9, 0x14] --> 0x0086C914
        self.is_virtual = is_virtual  # can use this class for real kinetek or simulator
        self.in_iap_mode = False
        self.hexUtil = HexUtility()

    

    # extract needed fw info from hex file 
    def load_hex_file(self, file_path):
        self.hexUtil.open_file(file_path)
        self.data_size_bytes = self.hexUtil.get_file_data_size()
        self.page_check_sums = self.hexUtil.get_page_checksums()
        self.total_checksum = self.hexUtil.get_total_checksum()
        self.total_checksum_reverse = self.total_checksum
        self.total_checksum_reverse.reverse()
        self.start_address = self.hexUtil.get_start_address()
        self.last_data_line_size = self.hexUtil.get_last_data_line_size()

        # make socket_can commands
        self.FW_REVISION_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("FW_REVISION_REQUEST"), get_kinetek_data_code("DEFAULT"))
        self.ENTER_IAP_MODE_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("ENTER_IAP_MODE"))
        self.SEND_BYTES_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("SEND_BYTES"))
        self.SEND_START_ADDRESS_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("CODE_START_ADDRESS_PREFIX") \
                                                                                                        + self.start_address
                                                                                                        + get_kinetek_data_code("CODE_START_ADDRESS_SUFFIX")
                                                                                                        )
        self.SEND_CHECKSUM_DATA_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("SEND_CHECKSUM_PREFIX") \
                                                                                                        + self.total_checksum
                                                                                                        + get_kinetek_data_code("SEND_CHECKSUM_SUFFIX")
                                                                                                        )
        self.SEND_DATA_SIZE_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("SEND_DATA_SIZE_PREFIX") \
                                                                                                        + list(self.data_size_bytes.to_bytes(4, "big"))
                                                                                                        + get_kinetek_data_code("SEND_DATA_SIZE_SUFFIX")
                                                                                                        )   

        self.SEND_EOF_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("END_OF_HEX_FILE_PREFIX") \
                                                                                                        + list(self.last_data_line_size.to_bytes(1, "big")) \
                                                                                                        + get_kinetek_data_code("END_OF_HEX_FILE_SUFFIX")
                                                                                                        )

        self.SEND_TOTAL_CHECKSUM_REQUEST = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("TOTAL_CHECKSUM_PREFIX") \
                                                                                                    + self.total_checksum_reverse \
                                                                                                    + get_kinetek_data_code("TOTAL_CHECKSUM_SUFFIX")
                                                                                                    )                                                                                  
        


    def print(self):
        print("\n")
        print("\t\t\t\t\t=============================================")
        print("\t\t\t\t\t============= IAP UTILITY PRINT== ===========")
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
        print("\t\t\t\t\t============= IAP UTILITY PRINT =============")
        print("\t\t\t\t\t=============================================\n\n\n\n\n\n\n")
    
    


    # send the kinetek an iap request, if expected response is received within the timeout thresh, then return True, otherwise false
    # request should be in socket_can form, expected_response should be string from lookup table in kinetekCodes
    def send_request(self, request, expected_response, timeout_count):
        if request != None: # if pass in none then just want to wait for a certain message from the kinetek
            self.bus.send(request)  
            print("SENT:\t", request)
        resp = self.bus.recv(timeout=1000)
        print("RECEIVED:\t", resp)
        count = 0
        
        # receive messages until either the expected one is received or timeout_count is up
        while lookup(decode_socketcan_packet(resp), IAP_data_lookup) != expected_response:
            if count > timeout_count:
                return False
            resp = self.bus.recv(timeout=1000)
            print("RECEIVED:\t", resp) 
            count += 1
        return True



    # send a request multiple times, with each request having a timeout causing the next attempt to send
    def send_request_repeated(self, request, expected_response, time_out_count, max_tries, timeout_message):
        num_tries = 0 # number of times request sent
        request_status = self.send_request(request, expected_response, time_out_count)
        while request_status == False: # keep sending request until reach max tries
            request_status = self.send_request(request, expected_response, time_out_count)
            if max_tries > 0: # if want to send request indefinetly then max_tries = -1 so don't increment num_tries
                num_tries +=1
            if num_tries > max_tries and max_tries > 0:
                return (False, timeout_message) 
        return None



    # start up can bus
    def init_can(self, channel_name):
        # need to add modprobe, ip set up stuff for ifconfig
        if self.is_virtual:
            self.bus = can.interface.Bus(bustype='socketcan', channel=channel_name)
        else:
            self.bus = can.interface.Bus(bustype='socketcan', channel=channel_name)



    # repeatedly send the enter iap mode command until get response from Kinetek to confirm in IAP mode
    def put_in_IAP_mode(self):
        self.send_request_repeated(self.ENTER_IAP_MODE_REQUEST, "ENTER_IAP_MODE_RESPONSE", -1, -1, None) # -1 ensures request sent indefinetely
        # no need to check response because it will request will only return if successful
        self.in_iap_mode = True
        return True
        print("entered iap_mode")



    def check_if_in_iap_mode(self): 
        self.in_iap_mode = self.send_request(None, "ENTER_IAP_MODE_RESPONSE", 20)
        if self.in_iap_mode == True:
            return "In IAP mode"
        return "Not in IAP mode"



    def send_init_packets(self):
        print("\n======= sending init packets =======\n")
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
        print("\n======= Uploading Hex File =======\n")
        self.page_count = 0 # page = 32 packets = 1024 bytes
        self.packet_count = 0 # packet = 32 bytes (4 can frames)
        self.current_packet = [] # store last four messages in case need to resend them
        write_ids = [0x04F, 0x050, 0x051, 0x052] # can ids for sending hex packet (4 can frames)   
        write_ids_retry = [0x053, 0x054, 0x055, 0x056] # can ids for resending hex packet
        self.num_bytes_uploaded = 0
        
        # keep uploading packets until reach end of hex file or timeout
        while True:
            # first check if reached end of page, have sent 32 packets
            if self.packet_count > 0 and self.packet_count% 32 == 0: # page_cs packet needs to be made while running unless want to make all during load
                print("\n======END OF PAGE======\n")
                page_cs = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                        + self.page_check_sums[self.page_count]
                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                        + list((self.page_count+1).to_bytes(1,"big")) \
                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                        )
                # the kinetek sends the packet checksum upon receiving 32 packets
                # you can check it but it tends to timeout so it is commented out

                # resp = self.send_request(None, "SELF_CALCULATED_PAGE_CHECKSUM", 40)
                # if resp == False:
                #     return "SLEF CHECKSUM NOT CALCULATED"
                
                # send the kinetek the correct page checksum and see if it responds correctly, if not return timeout message
                resp = self.send_request_repeated(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10, 2, "PAGE_CHECKSUM_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                self.page_count += 1


            # next send the next hex packet
            status = self.send_hex_packet(write_ids)
            if status == True: # keep sending hex packets until status false or none
                self.packet_count += 1
            
            # if the kinetek does not send confirmation, resend the packet
            elif status == False:
                status = self.send_hex_packet(write_ids_retry, True)
                if status == False:
                    return (False, "32_BYTE_RESPONSE_TIMEOUT")
                for chunk in self.current_packet:
                    self.num_bytes_uploaded += len(chunk)
                print(self.num_bytes_uploaded)
                self.packet_count += 1
                self.current_packet.clear() # if receive confirmation can clear and return true
                continue
                
            # if the return value is non then have reached end of file
            elif status == None: 
                page_cs = make_socketcan_frame(get_kinetek_can_id_code("IAP_REQUEST"), get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                        + self.page_check_sums[self.page_count]
                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                        + list((self.page_count+1).to_bytes(1,"big")) \
                                                                                        + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                        )
                # tell the kinetek reached end of hex file
                resp = self.send_request_repeated(self.SEND_EOF_REQUEST, "END_OF_HEX_FILE_RESPONSE", 10, 2, "END_OF_HEX_FILE_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                
                # can wait for last page cs if want to but tends to time out so commented out code
                # resp = self.send_request(None, "SELF_CALCULATED_PAGE_CHECKSUM", 40)
                # if resp == False:
                #     return "SLEF CHECKSUM NOT CALCULATED"
                
                # check that the last page checksum is correct (may be an incomplete page that does not land on 32 packets)
                resp = self.send_request_repeated(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10, 2, "PAGE_CHECKSUM_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]

                # check the total hex file checksum
                resp = self.send_request_repeated(self.SEND_TOTAL_CHECKSUM_REQUEST, "CALCULATE_TOTAL_CHECKSUM_RESPONSE", 10, 2, "TOTAL_CHECKSUM_TIMEOUT")
                if resp != None and resp[0] == False:
                    return resp[1]
                return (True, "EOF")
            
            
            
    # send four can frames, 32 bytes of data
    def send_hex_packet(self,write_ids, is_retry=False):
        # if this is a retry packet, want to resend the current packet instead of reading from hex file
        if is_retry == True:
            count = 0
            while True:
                hex_frame = make_socketcan_frame(write_ids[count], self.current_packet[count])
                if count == 3:
                    if self.send_request(hex_frame, "RECEIVED_32__BYTES", 80) == False: # if no confirmation, return false
                        return False
                    return True

                else:
                    self.bus.send(hex_frame) 
                    print("SENT:\t",hex_frame)
                count += 1

        # if this is a normal packet follow these steps
        write_id_index = 0
        while True:

            # if we have uploaded all data bytes then can return
            if self.num_bytes_uploaded == self.data_size_bytes:
                return None
            
            # get the next 8 data bytes from the hex file, or next n if last line and incomplete
            data = self.hexUtil.get_next_data_8() 
            
            # if this data is the last line then add filler if necessary
            if self.hexUtil.curr_line_index-1 == self.hexUtil.last_data_line_index: 
                print("\n\n\n====FILLER====\n\n\n")
                self.num_bytes_uploaded += len(data)
                last_data_frame_filler_amount = 8 - len(data) # complete the frame with filler data bytes
                if write_id_index == 0 and last_data_frame_filler_amount == 8: # if file ends on complete packet, don't think I need this because only way these conditions are true is if this was not a data line, so would not get here anyways, or an empty data line which does not make sense
                    return None

                # fill the last data frame with filler
                for i in range(last_data_frame_filler_amount):
                    data.append(0xFF)
                self.current_packet.append(data)

                # fill the last packet with filler frames
                filler_data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                num_frames_to_fill = 4 - len(self.current_packet) # complete the packet with filler frames
                for i in range(num_frames_to_fill):
                    self.current_packet.append(filler_data)

                # finally send the packet
                hex_frame = make_socketcan_frame(write_ids[write_id_index], self.current_packet[write_id_index])
                self.bus.send(hex_frame)
                print("SENT:\t", hex_frame)
                for i in range(num_frames_to_fill):
                    hex_frame = make_socketcan_frame(write_ids[write_id_index + i + 1], self.current_packet[write_id_index + i + 1])
                    if write_id_index + i + 1 == 3:
                        if self.send_request(hex_frame, "RECEIVED_32__BYTES", 40) == False: # if no confirmation, return false
                            return False
                        print(self.current_packet)
                        return None
                    self.bus.send(hex_frame)
                    print("SENT:\t", hex_frame)
                    

            # stores data in the current packet in case need to resend packet
            self.current_packet.append(data)
            if data == -1: # means eof so break loop
                self.upload_done = True
                return None

            hex_frame = make_socketcan_frame(write_ids[write_id_index],data)
            if write_id_index == 3: # if this is the fourth packet, wait for 32 bytes confirmation from Kinetek
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
                print("SENT:\t",hex_frame)

            write_id_index += 1
            if write_id_index == len(write_ids):
                write_id_index = 0



# translate socketcan frame into string format that can compare against
def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3) # form: "060"
    data = ""
    for byte in frame.data:
        data += hex(byte)[2:].zfill(2).upper() + " " # form: "00 00 00 00 00 00 00 00"
    return str(can_id + " | " + data[:-1])
