import argparse
from decoder import *
import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
from HexUtility import *
from IAPUtil import IAPUtil
from KinetekCodes import *

def send_request(request, expected_response, timeout_count):
        #self.bus.send(request)  
        #resp = self.bus.recv(timeout=1000)
        print("SENT:\t", request)
        resp = kin_socketcan.decode_frame(request)
        print("RECEIVED:\t", resp)
        count = 0
        while lookup(decode_socket(resp), IAP_data_lookup) != expected_response:
            #resp = self.bus.recv(timeout=1000)
            resp = kin_socketcan.decode_frame(request)
            print("RECEIVED:\t", resp) 
            count += 1
            if count > timeout_count:
                return False
        return True

    
def upload_image():
    global page_count
    global iapUtil
    global packet_count
    print("sending hex file...")
    #self.current_packet = [] # store in case need to retry
    write_ids = [0x04F, 0x050, 0x051, 0x052]     
    write_ids_retry = [0x053, 0x054, 0x055, 0x056]
    
    while True:
        status = send_hex_packet(write_ids)
        while status == True: # keep sending hex packets until status false or none
            packet_count +=1
            if packet_count % 32 == 0:
                page_cs = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                    get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                                    + iapUtil.page_check_sums[page_count] \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                                    + format_int_to_code(page_count+1, 1) \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                                    ))
                timeout_temp = 0 
                page_count += 1                                                                                   
                while send_request(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10) == False:
                    send_request(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10)
                    timeout_temp +=1
                    if timeout_temp > 2:
                        return (False, "PAGE_CHECKSUM_TIMEOUT")
            status = send_hex_packet(write_ids)
        if status == None: # reached end of file
            SEND_EOF = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("END_OF_HEX_FILE")))
            #print(SEND_EOF)
            page_cs = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                    get_kinetek_data_code("PAGE_CHECKSUM_PREFIX") \
                                                                                                    + iapUtil.page_check_sums[page_count] \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_MID") \
                                                                                                    + format_int_to_code(page_count+1, 1) \
                                                                                                    + get_kinetek_data_code("PAGE_CHECKSUM_SUFFIX")
                                                                                                    ))
            TOTAL_CHECKSUM = make_socketcan_packet(get_kinetek_can_id_code("IAP_REQUEST"), data_string_to_byte_list( \
                                                                                                    get_kinetek_data_code("TOTAL_CHECKSUM_PREFIX") \
                                                                                                    + reverse_bytes(iapUtil.total_checksum_reverse) \
                                                                                                    + get_kinetek_data_code("TOTAL_CHECKSUM_SUFFIX")
                                                                                                    ))
                                                                
            timeout_temp = 0 
            page_count += 1
            while send_request(SEND_EOF, "END_OF_HEX_FILE_RESPONSE", 10) == False:
                send_request(SEND_EOF, "END_OF_HEX_FILE_RESPONSE", 10)
                timeout_temp +=1
                if timeout_temp > 2:
                    return (False, "END_OF_HEX_FILE_TIMEOUT") 
            timeout_temp = 0                                                                                  
            while send_request(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10) == False:
                send_request(page_cs, "CALCULATE_PAGE_CHECKSUM_RESPONSE", 10)
                timeout_temp +=1
                if timeout_temp > 2:
                    return (False, "PAGE_CHECKSUM_TIMEOUT")
            timeout_temp = 0
            while send_request(TOTAL_CHECKSUM, "CALCULATE_TOTAL_CHECKSUM_RESPONSE", 10) == False:
                send_request(TOTAL_CHECKSUM, "CALCULATE_TOTAL_CHECKSUM_RESPONSE", 10)
                timeout_temp +=1
                if timeout_temp > 2:
                    return (False, "TOTAL_CHECKSUM_TIMEOUT")
        return (True, "EOF")
        if status == False: # retry
            status = send_hex_packet(write_ids_retry)
            if status == False:
                return (False, "32_BYTE_RESPONSE_TIMEOUT")
            continue

    
def send_hex_packet(write_ids): #32 bytes of data
    i = 0
    while True:
        data = iapUtil.hexUtil.get_next_data_8() # get the next 8 data bytes from the hex file
        #self.current_packet.append(data) # stores these in case need to retry
        current_packet.append(data)
        if data == -1: # means eof so break loop
            upload_done = True
            return None
        
        hex_frame = make_socketcan_packet(write_ids[i],data) # make a socket_can packet from hex data
        if i == 3: # if this is the fourth packet, ait for 32 bytes confirmation from Kinetek
            if send_request(hex_frame, "RECEIVED_32__BYTES", 20) == False: # if no confirmation, return false
                return False
            current_packet.clear # if receive confirmation can clear and return true
            return True

        else: # if first three packets then send normally
            #self.bus.send(hex_frame) 
            print("SENT:\t", hex_frame)
            resp = kin_socketcan.decode_frame(hex_frame)

        i += 1
        if i == len(write_ids):
            i = 0

def decode_socket(frame): # only accounts for id a data
        can_id = hex(frame.arbitration_id)[2:].zfill(3)
        data = ""
        for byte in frame.data:
           data += hex(byte)[2:].zfill(2).upper() + " "
        return str(can_id + " | " + data[:-1])




#========================= MAIN ========================================



if __name__ == "__main__":

    #----------------------csv test----------------
    # reads the iap commands from a csv file and responds like a kinetek, can compare with responses in csv


    # kin_csv = Decoder("csv") # make a csv decoder
   
    # # pass in the file to parse as a command line arg
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--csv_file", required=True)
    # args = parser.parse_args()
    # file_name = args.csv_file

    # read through the entire csv file line by line and get the decoder response
    # with open(file_name, 'r') as csv_file:
    #     reader = csv.reader(csv_file)
    #     for row in reader:
    #         response = kin_csv.decode_frame(row)
    #         if response != None: # the commands that are not IAP will return none
    #             print(response)
    #     print(kin_csv.hex_data) # recreated hex file



    # #----------------------socket_can test--------------------
    # behaves very similarly to the kinetek during iap, can be used to test instead of actual kinetek (takes in and returns socket_can frames)
    # just use the iap utility class to load in hex file information that can be "written" to the decoder

    # note calling the decode function multiple times may cause duplication
    # of the recreated hex data. Store return values in a variable as shown. It is like sending the kinetek a fw write twice.

    
    # make a kinetek socketcan decoder (make a kinetek simulator)
    kin_socketcan = Decoder("socketcan")
    print("start")

    # the IAP download utility which helps automates the process 
    iapUtil = IAPUtil()

    # extracts all needed iap information from hex file like checksum, size, start address. Also reads this file while hex data uploaded
    iapUtil.load_hex_file("/home/geffen.cooper/Desktop/kinetek_scripts/hex_file_copies/2.28_copy.hex")
    iapUtil.to_string() # print important hexfile data

    # send enter IAP mode command
    msg = can.Message(arbitration_id=0x048, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "060 | 08 00 00 00 00":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("entered IAP mode")
    
    # ask kinetek if can start sending data bytes
    msg = can.Message(arbitration_id=0x048, data=[0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 99 99 99 99 99 99 99 99":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("can start sending bytes")

    msg = can.Message(arbitration_id=0x048, data=[0x02, 0x08, 0x00, 0x80, 0x00, 0x9A, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 02 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)
    
    print("start address received")

    msg = can.Message(arbitration_id=0x048, data=[0x03, 0x00, 0x87, 0x47, 0xFE, 0x9B, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 03 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("checksum data received")

    msg = can.Message(arbitration_id=0x048, data=[0x04, 0x00, 0x01, 0x68, 0x30, 0x9C, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 04 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("code data size received")
    print("ready to start sending hex")
    # start reading and writing the binary file here
    


   
    
    current_packet = []
    page_count = 0
    packet_count = 0

    
    print("uploading")

    upload_image()

    print("\n\n Recreation of Hex file")

    print(kin_socketcan.hex_data)
    
        