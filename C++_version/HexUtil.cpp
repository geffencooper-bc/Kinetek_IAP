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
}

HexUtility::~HexUtility()
{
    hex_file.close();
}

int HexUtility::get_record_data_length(const string &hex_line)
{
    return stoi(hex_line.substr(RECORD_DATA_LENGTH_START_I, 2), 0, 16);
}

int HexUtility::get_record_address(const string &hex_line)
{
    return stoi(hex_line.substr(RECORD_ADDRESS_START_I, 4), 0, 16);
}

hex_record_type HexUtility::get_record_type(const string &hex_line)
{
    return (hex_record_type)(stoi(hex_line.substr(RECORD_TYPE_START_I,2), 0, 16));
}

void HexUtility::data_string_to_byte_list(const string &hex_line, uint8_t* data)
{
    for(int i = 0; i < hex_line.size(); i+=2)
    {
        data[i/2] = stoi(hex_line.substr(i,2), 0, 16);
    }
}

void HexUtility::get_record_data_bytes(const string &hex_line, uint8_t* data, int start, int num_bytes)
{
    start *= 2;
    string data_bytes = hex_line.substr(RECORD_DATA_START_I, 2*get_record_data_length(hex_line));
    if( (num_bytes == -1) || (data_bytes.size() < num_bytes) )
    {
        data_string_to_byte_list(data_bytes, data);
    }
    else
    {
        data_string_to_byte_list(hex_line.substr(RECORD_DATA_START_I, num_bytes), data);
    }
}

int HexUtility::get_record_checksum(const string &hex_line)
{
    return stoi(hex_line.substr(RECORD_DATA_START_I + 2*get_record_data_length(hex_line), 2), 0, 16);
}

int HexUtility::get_file_data_size()
{
    int size = 0;
    string last_line = "";
    while(getline(hex_file, curr_line))
    {
        if(get_record_type(curr_line) == DATA)
        {
            size += get_record_data_length(curr_line);
            last_line = curr_line;
        }
    }

    last_data_line_size = get_record_data_length(last_line);

    // reset pointer to top of file
    hex_file.clear();
    hex_file.seekg(0, ios::beg);
    return size;
}

void HexUtility::calc_laurence_checksum(uint8_t* data_bytes, size_t num_data_bytes, uint8_t* cs_bytes)
{
    uint32_t cs = 0;
    size_t i;
    for(i = 0; i < num_data_bytes; i++)
    {
        cs += data_bytes[i];
    }
    for(i = 0; i < KT_CHECKSUM_SIZE; i++)
    {
        cs_bytes[i] = cs & 0xFF;
        cs >> 8;
    }
}