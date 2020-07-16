#ifndef HEX_UTIL_H
#define HEX_UTIL_H

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdint.h>

using std::string;
using std::ifstream;

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
    END_OF_FILE = 1,
    EXTENDED_SEGMENT_AR = 2,
    EXTENDED_LINEAR_AR = 4,
    START_LINEAR_AR = 5
};

const uint8_t CAN_MAX_DATA_LEN = 8;
const uint8_t RECORD_DATA_LENGTH_START_I = 1;
const uint8_t RECORD_ADDRESS_START_I = 3;
const uint8_t RECORD_TYPE_START_I = 7;
const uint8_t RECORD_DATA_START_I = 9;
const uint8_t KT_CHECKSUM_SIZE = 4; // size in bytes

class HexUtility
{
    public:
    HexUtility(const string &hex_file_path);
    ~HexUtility();

    int get_record_data_length(const string &hex_line);
    int get_record_address(const string &hex_line);
    hex_record_type get_record_type(const string &hex_line);
    void get_record_data_bytes(const string &hex_line, uint8_t* data, int start=0, int num_bytes=-1);
    int get_record_checksum(const string &hex_line);

    int get_file_data_size();
    void calc_laurence_checksum(uint8_t* data_bytes, size_t num_data_bytes, uint8_t* cs_bytes);
    
    private:
    ifstream hex_file;
    string curr_line;
    bool is_first_8;
    bool is_eof;
    uint8_t last_data_line_size;

    void data_string_to_byte_list(const string &hex_line, uint8_t* data);
};

#endif