#ifndef HEX_UTIL_H
#define HEX_UTIL_H

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

using std::string;

// a utility class with helper functions to help read data from a hex file
// it relies on reading from a hex file and keeping the current position

// Hex file details

// Entries in hex files follow this format
//
// :llaaaatt[dd...dd]cc
//
// :          signifies the start of a line
// ll         signifies the number of bytes in the data record
// aaaa       signifies the address of this data field
// tt         signifies the record type
// [dd...dd]  signifies the data bytes
// cc         signifies the two byte checksum

enum hex_record_type
{
    DATA = 0,
    EOF = 1,
    EXTENDED_SEGMENT_AR = 2,
    EXTENDED_LINEAR_AR = 4,
    START_LINEAR_AR = 5
}


class HexUtility
{
    public:
    HexUtility();
    void open_file(string hex_file_path);
    int get_record_length(string hex_line);
    int get_record_address(string hex_line);
    hex_record_type get_record_type(string hex_line);
    void get_record_data_bytes(string hex_line, int start=0, int num_bytes=-1, uint8_t* data);
    int get_record_checksum(string hex_line);

    private:
    string hex_file_lines;
    size_t curr_line_index;
    bool is_first_8;
    bool is_eof;

    void data_string_to_bytes_list(string hex_line, uint8_t* data);
    //const uint8_t CAN_MAX_LEN = 8;
    
}

#endif