import csv
import re
import can
import hex_maker as hex_util
import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
from HexUtility import make_socketcan_packet, data_string_to_byte_list


# used for decoding requests/responses
IAP_data_lookup = [

    ('02\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s9A\s00\s00' ,    "send code start address"),
    ('03\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s9B\s00\s00' ,    "send code checksum data"),
    ('04\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s9C\s00\s00' ,    "send code data size"),
    ('05\s10\s10\s10\s10\s10\s10\s10',                                                             "send end of hex file message"),
    ('06\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s9D\s00\s00',     "send total checksum message"),
    ('07\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s9E\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]' , "check page checksum")
]

# a generic structure for a can frame to conform to from csv and socket can used by the decoder
class My_frame:
    def __init__(self, time_stamp, can_id, data):
        self.time_stamp = time_stamp
        self.can_id = can_id
        self.data = data


# a class used to make a decoder to recreate the hex file frame IAP CAN frames (imitates the Kinetek)
class Decoder:
    def __init__(self,input_type): # input is either "csv" or "socketcan"
        self.input_type = input_type
        self.hex_data = "" # stores the recreated hex file
        self.checksum_total = "" # stores the total check sum passed in by user
        self.data_size = "" # size of the fw file in bytes
        self.first_8 = "" # stores the first 8 bytes of a hex line passed in by can fram, gets merged with second 8
        self.curr_address = "" # holds the current address in the hex file (stored as total address, not just lower 16 bits of extended linear form)
        self.start_address = "" # holds the total start address in the hex file
        self.num_hex_frames = 0 # counts the number of hex can packets passed in (8 bytes)
        self.accumulated_hex_frames = "" # accumulates the hex frames passed in to calculate checksum
        self.accumulated_hex_frames_total = "" # same as above but total
        self.calc_checksum_total = "" # compare against passed in checksum
        self.calc_checksum_page = "" # same as above
        self.is_eof = False # if hex file ended received
        self.is_eop = False # if page ended
        self.noise_frame = make_socketcan_packet(0x101, data_string_to_byte_list("11 11 11 11 11 11 11 11"))
 

    # calculates the checksum of a page by adding all the bytes, need to convert from string, returns as the numerical value
    def calc_laurence_checksum(self,line):
        bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
        bytes_list_num = [int(i, 16) for i in bytes_list]
        return sum(bytes_list_num)
    
    # find the according pattern in the above table
    def lookup(self,data, table):
        for pattern, value in table:
            if re.search(pattern, data):
                return value
        return ""

    def init_simulator(self, channel_name):
        self.bus = can.interface.Bus(bustype='socketcan', channel=channel_name)

    def run_simulator(self):
        count = 0
        while True:
            frame = self.bus.recv(timeout=1000)
            print(frame)
            resp = self.decode_socketcan_frame(frame)
            if resp != None:
                self.bus.send(resp)
            count += 1
            if count % 10:
                self.spit_noise()

    # the kinetek spits rand messages, also helps iap with timeouts
    def spit_noise(self):
        self.bus.send(self.noise_frame)


    # takes the generic My_frame structure and decodes it by responding like a kinetek, input frames are commands sent during IAP
    def decode_my_frame(self, frame):
        #print(frame.can_id, " ", frame.data) # if want to see frames sent uncomment this (has lots of noise)
        print(frame.can_id)
        # ping command to see if working
        if frame.can_id == "0x0111":
            if frame.data == "11 11 11 11 11 11 11 11":
                return make_socketcan_packet(0x101, data_string_to_byte_list("10 10 10 10 10 10 10 10"))
        if frame.can_id == "0x0048": # IAP Request sent
            if frame.data == "00 00 00 00 00 00 00 00": # force enter IAP mode command
                return make_socketcan_packet(0x060, data_string_to_byte_list("80 00 00 00 00")) # entered IAP mode response

            elif frame.data == "88 88 88 88 88 88 88 88": # start sending bytes request
                return make_socketcan_packet(0x069, data_string_to_byte_list("99 99 99 99 99 99 99 99")) # ready to receive bytes response

            elif self.lookup(frame.data, IAP_data_lookup) == "send code start address": # send start address information
                self.start_address = frame.data[3:15].replace(" ","") # extract the start address from the frame
                self.curr_address = self.start_address # set this as the current address
                self.hex_data += hex_util.make_start_address(self.start_address) # use start address to add extended adress to hex file if necessary
                return make_socketcan_packet(0x069, data_string_to_byte_list("02 10 10 10 10 10 10 10"))

            elif self.lookup(frame.data, IAP_data_lookup) == "send code checksum data": # total checksum data
                self.checksum_total = frame.data[6:15].replace(" ", "") # extract the total checksum, no work done because don't have access to hex file yet
                return make_socketcan_packet(0x069, data_string_to_byte_list("03 10 10 10 10 10 10 10"))

            elif self.lookup(frame.data, IAP_data_lookup) == "send code data size": # not sure how kinetek uses this
                self.data_size = frame.data[6:17].replace(" ", "")
                return make_socketcan_packet(0x069, data_string_to_byte_list("04 10 10 10 10 10 10 10"))
            
            # the page checksum is calculated every 1024 bytes and is calculated in the frame_id 0x052 if block
            # that happens before this statement is called so we already have the checksum, just need to validate it
            elif self.lookup(frame.data, IAP_data_lookup) == "check page checksum": 
                print("\n\n\n=================================================\n\n\n")
                self.is_eop = True
                # calculate checksum of page, format into print frame
                self.accumulated_hex_frames = self.accumulated_hex_frames.replace(" ","")
                cs_page = hex(self.calc_laurence_checksum(self.accumulated_hex_frames))[2:].upper().zfill(6)
                self.calc_checksum_page = cs_page
                #print(self.accumulated_hex_frames)
                # rest values to start next page
                self.num_hex_frames = 0
                self.accumulated_hex_frames = ""  
                cs = frame.data[6:15].replace(" ", "")
                if cs == self.calc_checksum_page:
                    return make_socketcan_packet(0x069, data_string_to_byte_list("07 40 40 40 40 40 40 40"))
                else:
                    print(cs, " == ", self.calc_checksum_page)
                    return "wrong page checksum-------------------"
            
            # once the hex file ends, calculate total checksum, and current page checksum
            elif self.lookup(frame.data, IAP_data_lookup) == "send end of hex file message": 
                #print("==============EOF")
                self.is_eof = True
                self.accumulated_hex_frames_total = self.accumulated_hex_frames_total.replace(" ","")
                cs_total = hex(self.calc_laurence_checksum(self.accumulated_hex_frames_total))[2:].upper().zfill(6) # total checksum, format into string

                self.accumulated_hex_frames = self.accumulated_hex_frames.replace(" ","")
                cs_page = hex(self.calc_laurence_checksum(self.accumulated_hex_frames))[2:].upper().zfill(6) # current page checksum, format into string
                
                self.calc_checksum_page = cs_page
                self.calc_checksum_total = cs_total

                if self.calc_checksum_total == self.checksum_total: # check if total checksum good
                    return make_socketcan_packet(0x069, data_string_to_byte_list("05 20 20 20 20 20 20 20")) # need to return total checksum good
                else:
                    print(self.checksum_total, "!=", self.calc_checksum_total)
            
            elif self.lookup(frame.data, IAP_data_lookup) == "send total checksum message":
                #print("=TOTAL++++++++++++++++++++++")
                return make_socketcan_packet(0x069, data_string_to_byte_list("06 30 30 30 30 30 30 30"))
            
        elif self.is_eof == True:
                cs_page = self.calc_checksum_page
                cs_page = " ".join(cs_page[i:i+2] for i in range(0, len(cs_page), 2)) # format into print
                self.is_eof = False
                return (make_socketcan_packet(0x060, data_string_to_byte_list("84 00 " + cs_page)))

        if frame.can_id == "0x0045": # fw revision request
            if frame.data == "00 00 00 00 00 00 00 00": # default ?
                return make_socketcan_packet(0x067, data_string_to_byte_list("01 08 5E 00 80 00 00 00")) # fw revision response

        # hex file transfer commands, 4 sets of 8 bytes --> ids are 4F, 50, 51, 52 in that order   
        if frame.can_id == "0x004F" or frame.can_id == "0x004f":
            self.first_8 = frame.data # store first 8 bytes of 16 byte hex line
            if frame.data != "FF FF FF FF FF FF FF FF": # don't want to include empty space at end as part of hex file
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
            if self.is_eop == True:
                cs_page = self.calc_checksum_page
                cs_page = " ".join(cs_page[i:i+2] for i in range(0, len(cs_page), 2)) # format into print
                self.is_eop = False
                return (make_socketcan_packet(0x060, data_string_to_byte_list("84 00 " + cs_page)))
        elif frame.can_id == "0x0050":
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
            # second 8 bytes of 16 byte line received, combine it with first 8 bytes
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+frame.data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:] # increment the current address, then format to string
        elif frame.can_id == "0x0051": # same as 4F
            self.first_8 = frame.data
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
        elif frame.can_id == "0x0052":
            if frame.data != "FF FF FF FF FF FF FF FF": # first four lines same as 50 
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+frame.data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:]
            
            # keep track so can know when end of page, hex frame is 8 bytes
            self.num_hex_frames += 4 # this is the 4th 8 byte frame 
            return make_socketcan_packet(0x069, data_string_to_byte_list("10 10 10 10 10 10 10 10")) # 32 bytes received


    # takes in a csv frame, returns nothing if not an IAP frame, returns expected kinetek reply otherwise
    def decode_csv_frame(self, frame):
        TIME_STAMP = 2
        ID = 5
        DATA = 9

        my_frame = My_frame(frame[TIME_STAMP], frame[ID], frame[DATA][3:26])
        return self.decode_my_frame(my_frame)
            
    # takes in a socketcan frame and returns what would be expected for the kinetek (only IAP)
    def decode_socketcan_frame(self, frame):
        can_id = "0x" + hex(frame.arbitration_id)[2:].zfill(4)
        data = ""
        for byte in frame.data:
           data += hex(byte)[2:].zfill(2).upper() + " "
        my_frame = My_frame(frame.timestamp, can_id, data[:-1])
        return self.decode_my_frame(my_frame)

    # determines if csv or socketcan
    def decode_frame(self, frame):
        if self.input_type == "csv":
            return self.decode_csv_frame(frame)
        elif self.input_type == "socketcan":
            return self.decode_socketcan_frame(frame)

