#!/usr/bin/env python3

import can

# The following is a utility class with functions to help read data from a hex file
# It relies on reading from a hex file and keeps track of the current position


# Hex file details

# Entries in hex files follow this format
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

# hex record types
DATA = "00"
EXTENDED = "04"
EOF = "01"
START_LINEAR_ADDRESS = "05"

class HexUtility:
    def __init__(self):
        self.curr_line_index = 0 # current line reading from in hex file
        self.first_8 = True      # reading the first 8 or second 8 bytes
        self.is_eof = False

    # open a hex file and store all the lines into a string
    def open_file(self, hex_file_path): 
        self.hex_file_path = hex_file_path
        self.hex_file = open(self.hex_file_path, "r")
        self.hex_lines = self.hex_file.readlines()
    
 # the following five functions extract a certain field given an entry in the hex file
    
    # return: the length in integer form
    def get_record_length(self, line):
        return int(line[RECORD_LENGTH_FIELD],16)

    # return: the address in integer form
    def get_record_address(self, line):
        return int(line[ADDRESS_FIELD], 16)
    
    # return: type in string form
    def get_record_type(self, line):
        return line[TYPE_FIELD]
    
    # start is an index relative to the first byte, so 8 means start from the 8th byte, num_bytes is how many bytes after start you want to get
    # return: the data portion of a line in the hex file as a list of bytes, ex: "001122..." --> [0x00, 0x11, 0x22, ...]
    def get_record_data_bytes(self, line, start=0, num_bytes=-1): 
        start = start*2 # each byte is two hex digits                   012345678
        data_start = 9 # the data is guaranteed to start at index 9 --> :llaaaatt[dd...dd]cc
        if num_bytes == -1 or len(line[data_start:data_start + 2*self.get_record_length(line)]) < num_bytes:  # then get all bytes in line
            data_bytes = line[data_start+start:data_start+start + 2*self.get_record_length(line)] # record length in bytes, two hex chars are a byte
        else:
            data_bytes = line[data_start+start:data_start+start + 2*num_bytes]
        return data_string_to_byte_list(data_bytes)

    # not used for now, maybe later to verify hex file
    def get_record_checksum(self, line):
        return int(line[9 + 2*self.get_record_length(line):9 + 2*self.get_record_length(line) + 2], 16)

    # add up all the record lengths of data lines
    # return: number of data bytes as an int
    def get_file_data_size(self):
        size = 0
        for line in self.hex_lines:
            if self.get_record_type(line) == DATA:
                line_size = self.get_record_length(line)
                size += line_size
        return size
    
    # finds the last data line starting from the bottom
    # return: record length as an int
    def get_last_data_line_size(self):
        index = len(self.hex_lines) - 1
        while self.get_record_type(self.hex_lines[index]) != DATA:
            index -=1
        self.last_data_line_index = index
        return self.get_record_length(self.hex_lines[self.last_data_line_index])

    # input: a stream of bytes as a list, ex: [0x01, 0x02, 0x03, ...]
    # return: the sum of all bytes as a list of 4 bytes ex: [0xAA, 0xBB, 0xCC, 0xDD]
    def calc_laurence_checksum(self, line):
        cs = sum(line)
        return list(cs.to_bytes(4, "big"))

    # extracts a list of all data bytes in hex, gets their Laurence checksum
    # return: the sum of all bytes a list of 4 bytes ex: [0x00, 0x86, 0xC9, 0x14]
    def get_total_checksum(self):
        raw_data = []
        for line in self.hex_lines:
            if self.get_record_type(line) == DATA:
                raw_data += self.get_record_data_bytes(line)
        return self.calc_laurence_checksum(raw_data)

    # reads through entire file string and gets Laurence checksum every page (1024 bytes)
    # return: all page checksums as list of 4 bytes ex: [[0x00 0x01 0x23 0x4A], [0x00, 0x01, 0xC3, 0xB7], ...]
    def get_page_checksums(self):
        page_data = []
        page_check_sums = []
        i = 0
        for line in self.hex_lines:
            if self.get_record_type(line) == DATA:
                page_data += self.get_record_data_bytes(line)
                i += 1
                if i == 64: # pages are 1024 bytes, 128 frames * 8 bytes each --> 64 lines 16 bytes each
                    page_check_sums.append(self.calc_laurence_checksum(page_data))
                    page_data = []
                    i = 0
        page_check_sums.append(self.calc_laurence_checksum(page_data)) # the last remaining packets make up a degenarate page, lol
        return page_check_sums

    
    # gets the start address by parsing the first and/or second line, returns as string ex: "08008000"
    # return: the start address as a list of 4 bytes
    def get_start_address(self):
        first_line = self.hex_lines[0]
        if self.get_record_type(first_line) == EXTENDED: # if extended address
            top_16_bits = self.get_record_data_bytes(first_line) # top 16 bits stored in data bytes
            top_16_bits = top_16_bits[0] << 8 + top_16_bits[1] # need to convert from bytes list to int, ex: [0x01, 0x10] --> 0x0110
            second_line = self.hex_lines[1]
            if self.get_record_type(second_line) == DATA: # if the first data line
                bottom_16_bits = self.get_record_address(second_line)
                start_address = (top_16_bits << 16) + bottom_16_bits
                return list(start_address.to_bytes(4, "big"))
        return self.get_address(first_line)

    # calculates the checksum of an entry in the hex file (.hex checksum), not used currently but maybe later to verify hex file
    # return: the line checksum as an int
    def calc_hex_checksum(self, line):
        bytes_list = data_string_to_byte_list(line)
        two_compl = (256 - sum(bytes_list)) % 256
        return two_compl

    # used to get the next data bytes in the hex file based on the current line being read , returns -1 if eof
    def get_next_data_8(self):

        data_bytes = []
        curr_line = self.hex_lines[self.curr_line_index]
        record_type = self.get_record_type(self.hex_lines[self.curr_line_index])
        record_length = self.get_record_length(curr_line)

        # no more data lines
        if  record_type == EOF or record_type == START_LINEAR_ADDRESS:
            self.is_eof = True
            return -1
        
        # find next data line
        while record_type != DATA:
            self.curr_line_index +=1
            curr_line = self.hex_lines[self.curr_line_index]
            record_type = self.get_record_type(self.hex_lines[self.curr_line_index])
            record_length = self.get_record_length(curr_line)

        # last data line might be 4 bytes or 12 bytes
        if record_length < 8: 
            data_bytes = self.get_record_data_bytes(curr_line, 0, record_length) 
            self.curr_line_index += 1

        # check if reading the first or second 8 bytes in the 16 byte line, may need to change this if have hex files that are not 16 byte lines
        elif self.first_8:
            self.first_8 = False
            data_bytes = self.get_record_data_bytes(curr_line, 0, 8)

        else:
            self.first_8 = True
            data_bytes = self.get_record_data_bytes(curr_line, 8, 8) 
            self.curr_line_index +=1 # after read second 8 bytes, reached end of line
        
        return data_bytes

    def __del__(self):
        print("closing file")
        self.hex_file.close()

# additional helper functions not directly related to hex file, independent of class

# converts a byte string (spaced or unspaced) into a list of numerical bytes
# input: '00 01 02 A0 30 12 5C 10' --> outut: [0x00, 0x01, 0x02, 0xA0, 0x30, 0x12, 0x5C, 0x10]
def data_string_to_byte_list(data_bytes):
    data_bytes = data_bytes.replace(" ","")
    bytes_list = [data_bytes[i:i+2] for i in range(0, len(data_bytes), 2)]
    bytes_list_num = [int(i, 16) for i in bytes_list]
    return bytes_list_num

# make a sokcet can message from can id (int) and data bytes (list of bytes)
def make_socketcan_frame(can_id, data_bytes): # pass in data as a list of 8 bytes
    return can.Message(arbitration_id=can_id, data=data_bytes, is_extended_id=False)