#include "HexUtil.h"

using std::ifstream;
using std::ostringstream;
using std::stoi;
using std::ios;

HexUtility::HexUtility(const string &hex_file_path) 
{
    // need to init other member variables

    hex_file.open(hex_file_path);
    if(hex_file.fail())
    {
        printf("Invalid File Path\n");
        // need to quit
    }
    load_hex_file_data();
}

HexUtility::~HexUtility()
{
    hex_file.close();
}

void HexUtility::get_total_cs(uint8_t* cs_bytes, uint8_t num_cs_bytes)
{
    cs_to_byte_list(total_checksum, cs_bytes, num_cs_bytes);
}


//-------------- helper funcs

int HexUtility::get_record_data_length(const string &hex_record)
{
    return stoi(hex_record.substr(RECORD_DATA_LENGTH_START_I, 2), 0, 16);
}

int HexUtility::get_record_address(const string &hex_record)
{
    return stoi(hex_record.substr(RECORD_ADDRESS_START_I, 4), 0, 16);
}

hex_record_type HexUtility::get_record_type(const string &hex_record)
{
    return (hex_record_type)(stoi(hex_record.substr(RECORD_TYPE_START_I,2), 0, 16));
}

int HexUtility::data_string_to_byte_list(const string &hex_data, uint8_t* data_bytes, uint8_t num_data_bytes)
{
    // the number of bytes should be at least half the number of chars in the string, "AA" --> 1 byte
    if(num_data_bytes < hex_data.size()/2)
    {
        return -1;
    }
    // iterate through the string only filling in data bytes every two chars, return the sum of the bytes for checksum
    int sum_bytes = 0;
    for(int i = 0; i < hex_data.size(); i+=2)
    {
        data_bytes[i/2] = stoi(hex_data.substr(i,2), 0, 16);
        sum_bytes += data_bytes[i/2];
    }
    return sum_bytes;
}

int HexUtility::get_record_data_bytes(const string &hex_record, uint8_t* data_bytes, uint8_t num_data_bytes, int start, int num_bytes)
{
    // the buffer should be at least the size of the number of bytes to extract
    // otherwise it needs to be at least the size of the record length
    if( (num_data_bytes < num_bytes) || ( (num_bytes == -1) && num_data_bytes < get_record_data_length(hex_record)))
    {
        return -1;
    }
    
    start *= 2; // remember that number of chars = 2*number of bytes
    
    // get the data bytes as a string
    string data = hex_record.substr(RECORD_DATA_START_I, 2*get_record_data_length(hex_record));
    
    // if asking for too many bytes or default, then just grab the whole line (16 bytes)
    if( (num_bytes == -1) || (data.size() < 2*num_bytes) )
    {
        return data_string_to_byte_list(data, data_bytes, num_data_bytes);
    }
    else
    {
       return data_string_to_byte_list(hex_record.substr(RECORD_DATA_START_I, num_bytes), data_bytes, num_data_bytes);
    }
}

int HexUtility::get_record_checksum(const string &hex_line)
{
    return stoi(hex_line.substr(RECORD_DATA_START_I + 2*get_record_data_length(hex_line), 2), 0, 16);
}

int HexUtility::load_hex_file_data()
{
    string last_data_line = ""; // save the last data line so can get its size
    uint8_t byte_list[16];       // buffer to hold next 16 data bytes in the hex file
    while(getline(hex_file, curr_line))
    {
        if(get_record_type(curr_line) == DATA)
        {
            hex_file_data_size += get_record_data_length(curr_line);
            total_checksum += get_record_data_bytes(curr_line, byte_list, 16);

            last_data_line = curr_line;
        }
    }

    last_data_line_size = get_record_data_length(last_data_line);

    // reset pointer to top of file
    hex_file.clear();
    hex_file.seekg(0, ios::beg);
}

int HexUtility::cs_to_byte_list(uint32_t cs, uint8_t* cs_bytes, uint8_t num_cs_bytes)
{
    if(num_cs_bytes != KT_CHECKSUM_SIZE)
    {
        // exit
    }
    // need to convert checksum from number to list of bytes, ex: 0x00018C1D --> [0x00, 0x01, 0x8C, 0x1D]
    for(int i = 0; i < KT_CHECKSUM_SIZE; i++)
    {
        cs_bytes[i] = (cs >> 8*(KT_CHECKSUM_SIZE-i-1)) & 0xFF;
    }
}

