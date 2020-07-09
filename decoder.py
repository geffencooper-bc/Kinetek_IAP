import csv
import hexutils as hex_util
import re
import can


# used for decoding requests
IAP_data_lookup = [

    ('10 10 10 10 10 10 10 10' ,                                                            "received 32 bytes"),
    ('88 88 88 88 88 88 88 88' ,                                                            "start sending bytes request"),
    ('99 99 99 99 99 99 99 99' ,                                                            "ready to receive bytes response"),
    ('[0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 5E|5F [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 00 00 00' , "receive reply of version request command"),
    ('02 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9A 00 00' ,    "send code start address"),
    ('02 10 10 10 10 10 10 10' ,                                                            "receive reply of code start address"),
    ('03 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9B 00 00' ,    "send code checksum data"),
    ('03 10 10 10 10 10 10 10' ,                                                            "receive reply of code checksum"),
    ('04 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9C 00 00' ,    "send code data size"),
    ('04 10 10 10 10 10 10 10' ,                                                            "receive reply of code data size"),
    ('05 10 00 00 00 90 00 00' ,                                                            "send end of hex file message"),
    ('05 20 20 20 20 20 20 20' ,                                                            "calculated checksum successfully"),
    ('07 40 40 40 40 40 40 40' ,                                                            "checksum correct?"),
    ('07 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9E [0-9A-F][0-9A-F] [0-9A-F][0-9A-F]' , "check page checksum"),
    ('84 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F]',              "calculated page checksum")
] 

# a generic structure for a can frame to conform to from csv and socket can used by the decoder
class My_frame:
    def __init__(self, time_stamp, can_id, data):
        self.time_stamp = time_stamp
        self.can_id = can_id
        self.data = data

# a class used to make a decoder to recreate the hex file frame IAP CAN frames (imitates the Kinetek)
class Decoder:
    def __init__(self,input_type): # input is either csv or socketcan
        self.input_type = input_type
        self.hex_data = "" # stores the recreated hex file
        self.check_sum = "" # stores the total check sum passed in by user
        self.data_size = "" # size of the fw file in bytes
        self.first_8 = "" # stores the first 8 bytes of a hex line passed in by can fram, gets merged with second 8
        self.curr_address = "" # holds the current address in the hex file
        self.start_address = "" # holds the start address in the hex file
        self.num_hex_frames = 0 # counts the number of hex can packets passed in (8 bytes)
        self.accumulated_hex_frames = "" # accumulates the hex frames passed in to calculate checksum
        self.accumulated_hex_frames_total = "" # same as above but total
        self.calc_checksum_total = "" # compare against passed in checksum
        self.calc_checksum_page = "" # same as above
 

    # calculates the checksum of a page by adding all the bytes, need to convert from string
    def calc_page_checksum(self,line):
        bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
        #print(bytes_list)
        #print(len(bytes_list))
        bytes_list_num = [int(i, 16) for i in bytes_list]
        return sum(bytes_list_num)
    
    # find the according pattern in the above table
    def lookup(self,data, table):
        for pattern, value in table:
            if re.search(pattern, data):
                return value
        return ""

    def decode_my_frame(self, frame):
        #print(frame.can_id, " ", frame.data) # if want to see frames sent uncomment this (has lots of noise)
        if frame.can_id == "0x0048": # IAP Request sent
            if frame.data == "00 00 00 00 00 00 00 00": # force enter IAP mode command
                return "0x0060 | 0x05 | 08 00 00 00 00" # entered IAP mode response

            elif frame.data == "88 88 88 88 88 88 88 88": # start sending bytes request
                return "0x0069 | 0x08 | 99 99 99 99 99 99 99 99" # ready to receive bytes response

            elif self.lookup(frame.data, IAP_data_lookup) == "send code start address": # send start address information
                self.start_address = frame.data[3:15].replace(" ","") # extract the start address from the frame
                self.curr_address = self.start_address # set this as the current address
                self.hex_data += hex_util.make_start_address(self.start_address) # use start address to add extended adress to hex file if necessary
               
                return "0x0069 | 0x08 | 02 10 10 10 10 10 10 10"

            elif self.lookup(frame.data, IAP_data_lookup) == "send code checksum data": # total checksum data
                self.check_sum = frame.data[6:15].replace(" ", "") # extract the total checksum
                return "0x0069 | 0x08 | 03 10 10 10 10 10 10 10"

            elif self.lookup(frame.data, IAP_data_lookup) == "send code data size": # not really used
                self.data_size = frame.data[6:17].replace(" ", "")
                return "0x0069 | 0x08 | 04 10 10 10 10 10 10 10"

            elif self.lookup(frame.data, IAP_data_lookup) == "check page checksum": # compare last calculated page checksum to value fed in
                cks = frame.data[6:15].replace(" ", "")
                if cks == self.calc_checksum_page:
                    return "0x0069 | 0x08 | 07 40 40 40 40 40 40 40"
                else:
                    print(cks, " == ", self.calc_checksum_page)
                    return "wrong page checksum-------------------"
            
            elif self.lookup(frame.data, IAP_data_lookup) == "send end of hex file message": # once the hex file ends, calculate total checksum, and current checksum
                self.accumulated_hex_frames_total = self.accumulated_hex_frames_total.replace(" ","")
                cs = hex(self.calc_page_checksum(self.accumulated_hex_frames_total))[2:].upper().zfill(6)

                self.accumulated_hex_frames = self.accumulated_hex_frames.replace(" ","")
                cs_page = hex(self.calc_page_checksum(self.accumulated_hex_frames))[2:].upper().zfill(6)
                
                self.calc_checksum_page = cs_page
                self.calc_checksum_total = cs

                cs_page = " ".join(cs_page[i:i+2] for i in range(0, len(cs_page), 2))
                if self.calc_checksum_total == self.check_sum: # check if total checksum good
                    return "0x0069 | 0x08 | 05 20 20 20 20 20 20 20" + "\n0x0060 | 0x08 | 84 00 " + cs_page
                else:
                    print(self.check_sum, "!=", self.calc_checksum_total)

        if frame.can_id == "0x0045": # fw revision request
            if frame.data == "00 00 00 00 00 00 00 00": # force enter IAP mode
                return "0x0067 | 0x08 | 01 08 5E 00 80 00 00 00" # fw revision response

        # hex file transfer        
        if frame.can_id == "0x004F" or frame.can_id == "0x004f":
            self.first_8 = frame.data
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
        elif frame.can_id == "0x0050":
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+frame.data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:]
        elif frame.can_id == "0x0051":
            self.first_8 = frame.data
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
        elif frame.can_id == "0x0052":
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+frame.data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:]
            self.num_hex_frames += 4
            if frame.data != "FF FF FF FF FF FF FF FF":
                self.accumulated_hex_frames += frame.data
                self.accumulated_hex_frames_total += frame.data
            return_msg = "0x0069 | 0x08 | 10 10 10 10 10 10 10 10" # 32 bytes received
            if self.num_hex_frames == 128:
                self.accumulated_hex_frames = self.accumulated_hex_frames.replace(" ","")
                return_msg += "\n" + "0x0060 | 0x05 | 84 00 "
                cs = hex(self.calc_page_checksum(self.accumulated_hex_frames))[2:].upper().zfill(6)
                cs = " ".join(cs[i:i+2] for i in range(0, len(cs), 2))
                return_msg += cs
                self.calc_checksum_page = cs.replace(" ","")
                self.num_hex_frames = 0
                self.accumulated_hex_frames = ""
                return return_msg      
            return return_msg


    # takes in a csv frame, returns nothing if not an IAP frame, returns expected kinetek reply otherwise
    def decode_csv_frame(self, frame):
        TIME_STAMP = 2
        ID = 5
        DATA = 9

        my_frame = My_frame(frame[TIME_STAMP], frame[ID], frame[DATA][3:26])
        return self.decode_my_frame(my_frame)
            
    # takes in a socketcan frame and returns what would be expected for the kinetek (only IAP)
    def decode_socketcan_frame(self, frame):
        can_id = "0x00" + hex(frame.arbitration_id)[2:]
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

