import csv
import argparse
import hexutils as hex_util
import re

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
        ('04 10 10 10 10 10 10 10' ,                                                            "receive reply of code checksum data"),
        ('05 10 00 00 00 90 00 00' ,                                                            "send end of hex file message"),
        ('05 20 20 20 20 20 20 20' ,                                                            "calculated checksum successfully"),
    ] 

# a class used to make a decoder to recreate the hex file frame IAP CAN frames (imitates the Kinetek)
class Decoder:
    def __init__(self,input_type): # input is either csv or socketcan
        self.input_type = input_type
        self.hex_data = ""
        self.check_sum = ""
        self.data_size = ""
        self.first_8 = ""
        self.curr_address = ""
        self.start_address = ""
        # self.can_input_frame = ""
        # self.initial_state()
    
    # def get_next_frame(self)

    # def initial_state(self):
    #     while(decode_frame(get_next_frame()) != "0x0048 | 0x08 | 08 00 00 00 00 00 00 00"): # force enter iap mode command
    #         print("Decoded frame: still in inital state, waiting till enter IAP_MODE, getting next frame")
    #     print("Decoded frame: ENTERED IAP MODE, getting next frame")
    #     self.iap_state_1()

    # def iap_state_1(self): # before fw revision request
    #     while(decode_frame(get_next_frame()) != "0x0045 | 0x00 | 00 00 00 00 00"): # fw revision request
    #         print("Decoded frame: in iap mode, getting next frame")
    #     print("Decoded frame: FW REVISION REQUEST COMMAND, getting next frame")
    #     self.iap_state_1()

    # use regex for IAP data because is different for each fw version
    

    # find the according pattern in the above table
    def lookup(self,data, table):
        for pattern, value in table:
            if re.search(pattern, data):
                return value
        return ""

    def decode_csv_frame(self, frame):
        ID = 5
        DATA = 9
        data = frame[DATA][3:26]
        if frame[ID] == "0x0048": # IAP Request
            #print("IAP REQ")
            if data == "00 00 00 00 00 00 00 00": # force enter IAP mode
                return "0x0060 | 0x05 | 08 00 00 00 00" # entered IAP mode
            elif data == "88 88 88 88 88 88 88 88": # start sending bytes request
                return "0x0069 | 0x08 | 99 99 99 99 99 99 99 99" # ready to receive bytes
            elif self.lookup(data, IAP_data_lookup) == "send code start address": # send start address
                #print("ad", data[3:15])
                self.start_address = data[3:15].replace(" ","")
                self.curr_address = self.start_address
                self.hex_data += hex_util.make_start_address(self.start_address) # use start address to add extended adress to hex file if necessary
                return "0x0069 | 0x08 | 02 10 10 10 10 10 10 10"
            elif data == "03 00 87 47 FE 9B 00 00": # checksum data
                self.check_sum = data[6:17].replace(" ", "")
                return "0x0069 | 0x08 | 03 10 10 10 10 10 10 10"
            elif data == self.lookup(data, IAP_data_lookup) == "send code data size":
                self.data_size = data[6:17].replace(" ", "")
                return "04 10 10 10 10 10 10 10"
        if frame[ID] == "0x0045": # fw revision request
            if frame[DATA][3:26] == "00 00 00 00 00 00 00 00": # force enter IAP mode
                return "0x0067 | 0x08 | 01 08 5E 00 80 00 00 00" # fw revision response
        if frame[ID] == "0x004F":
            #print("first 8 bytes", data)
            self.first_8 = data
        elif frame[ID] == "0x0050":
            #print("second 8 bytes", data)
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:]
        elif frame[ID] == "0x0051":
            #print("3rd 8 bytes", data)
            self.first_8 = data
        elif frame[ID] == "0x0052":
            #print("4th 8 bytes", data)
            self.hex_data += hex_util.make_line((self.first_8).replace(" ", "")+data.replace(" ", ""), self.curr_address)
            self.curr_address = hex(int(self.curr_address, 16) + 0x0010)[2:]
            
    def decode_socketcan_frame(self, frame):
        pass

    def decode_frame(self, frame):
        if self.input_type == "csv":
            return self.decode_csv_frame(frame)
        elif self.input_type == "socketcan":
            return self.decode_socketcan_frame(frame)

if __name__ == "__main__":
    kin_csv = Decoder("csv")
   
    # pass in the file to parse as a command line arg
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_file", required=True)
    args = parser.parse_args()
    file_name = args.csv_file

    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            response = kin_csv.decode_frame(row)
            if response != None:
                pass
                #print(response)
        print(kin_csv.hex_data)