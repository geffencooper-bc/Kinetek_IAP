#!/usr/bin/env python3

# lines in hex files follow this format
#
# :llaaaatt[dd...dd]cc
#
# :          signifies the start of a line
# ll         signifies the number of bytes in the data record
# aaaa       signifies the address of this data field
# tt         signifies the record type
# [dd...dd]  signifies the data bytes
# cc         signifies the two byte checksum

# hex data fields
RECORD_LENGTH_FIELD = slice(1,3)
ADDRESS_FIELD = slice(3,7)
TYPE_FIELD = slice(7,9)
# DATA_FIELD depends on record length
# CHECKSUM_FIELD depends on data length

class HexUtility:
    def __init__(self):
        self.curr_line = 0

    def open_file(self, hex_file_path):
        self.hex_file_path = hex_file_path
        self.hex_file = open(self.hex_file_path, "r")
        self.hex_lines = self.hex_file.readlines()
    
    def get_record_length(self, line):
        return line[RECORD_LENGTH_FIELD]

    def get_address(self, line):
        return line[ADDRESS_FIELD]
    
    def get_type(self, line):
        return line[TYPE_FIELD]

    def get_data_bytes(self, line):
        return line[9:9 + 2*int(self.get_record_length(line))] # record length in bytes, two hex chars are a byte

    def get_checksum(self, line):
        return line[9 + 2*int(self.get_record_length(line)):9 + 2*int(self.get_record_length(line)) + 2] # don't know if have newline or not, safer to start from begginging
    
    def get_start_address(self): # returns it as a string
        first_line = self.hex_lines[0]
        if self.get_type(first_line) == "04": # if extended address
            top_16_bits = self.get_data_bytes(first_line) # stored in data bytes
            second_line = self.hex_lines[1]
            if self.get_type(second_line) == "00": # if the first data line
                bottom_16_bits = self.get_address(second_line)
                start_address = top_16_bits + bottom_16_bits
                return start_address
        return self.get_address(first_line)
            
    def __del__(self):
        print("closing file")
        self.hex_file.close()
        

# for the actual can class make it easy to send messages, abstract away socket can
# for example can say "send data size __" or "send start address __" functions

# also make a translate function that translates socketcan messages

#also make function to read and translate hex file

# also make function to check timeout
hexUtil = HexUtility()
hexUtil.open_file("2.27_copy.hex")
print(hexUtil.get_start_address())