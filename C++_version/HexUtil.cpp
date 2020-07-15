#include "HexUtil.h"
#include <string.h>

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
}

int HexUtility::get_record_length(string hex_line)
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



void HexUtility::get_record_data_bytes(string hex_line, int start=0, int num_bytes=-1, uint8_t* data)
{
    start *= 2;
    int data_start = 9;
    string data_bytes = hex_line.substr(data_start, 2*get_record_length(hex_line));
    if( (num_bytes == -1) || (data_bytes.size() < num_bytes) )
    {
        
    }
}