#include "HexUtil.h"

using std::ifstream;
using std::ostringstream;
using std::stoi;

HexUtility::HexUtility()
{

}

void HexUtility::open_file(string hex_file_path)
{
    ifstream file(hex_file_path);
    ostringstream ss;
    ss << file.rdbuf();
    hex_file_lines = ss.str();
    file.close();
}

int HexUtility::get_record_data_length(string hex_line)
{
    return stoi(hex_line.substr(1, 2), 0, 16);
}

int HexUtility::get_record_address(string hex_line)
{
    return stoi(hex_line.substr(3, 4), 0, 16);
}

hex_record_type HexUtility::get_record_type(string hex_line)
{
    return (hex_record_type)(stoi(hex_line.substr(7,2), 0, 16));
}

void HexUtility::data_string_to_byte_list(string hex_line, uint8_t* data)
{
    for(int i = 0; i < hex_line.size(); i+=2)
    {
        data[i/2] = stoi(hex_line.substr(i,2), 0, 16);
    }
}

void HexUtility::get_record_data_bytes(string hex_line, uint8_t* data, int start, int num_bytes)
{
    start *= 2;
    string data_bytes = hex_line.substr(HEX_DATA_START_I, 2*get_record_data_length(hex_line));
    if( (num_bytes == -1) || (data_bytes.size() < num_bytes) )
    {
        data_string_to_byte_list(data_bytes, data);
    }
    else
    {
        data_string_to_byte_list(hex_line.substr(HEX_DATA_START_I, num_bytes), data);
    }
}