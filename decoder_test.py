import argparse
from decoder import *
import hexutils as hexutil

from HexUtility import *

def calc_page_checksum(line):
    bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
    print(bytes_list)
    print(len(bytes_list))
    bytes_list_num = [int(i, 16) for i in bytes_list]
    return sum(bytes_list_num)

if __name__ == "__main__":
    #----------------------csv test----------------
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




    # #----------------------socket_can test--------------------
    # kin_socketcan = Decoder("socketcan")
    # msg = can.Message(arbitration_id=0x048, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    # while kin_socketcan.decode_frame(msg) != "0x0060 | 0x05 | 08 00 00 00 00":
    #     print(kin_socketcan.decode_frame(msg))

    # print("entered IAP mode")
    
    # msg = can.Message(arbitration_id=0x048, data=[0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88], is_extended_id=False)
    # while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 99 99 99 99 99 99 99 99":
    #     print(kin_socketcan.decode_frame(msg))

    # print("can start sending bytes")

    # msg = can.Message(arbitration_id=0x048, data=[0x02, 0x08, 0x00, 0x80, 0x00, 0x9A, 0x00, 0x00], is_extended_id=False)
    # while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 02 10 10 10 10 10 10 10":
    #     print(kin_socketcan.decode_frame(msg))
    
    # print("start address received")

    # msg = can.Message(arbitration_id=0x048, data=[0x03, 0x00, 0x87, 0x47, 0xFE, 0x9B, 0x00, 0x00], is_extended_id=False)
    # while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 03 10 10 10 10 10 10 10":
    #    print(kin_socketcan.decode_frame(msg))

    # print("checksum data received")

    # msg = can.Message(arbitration_id=0x048, data=[0x04, 0x00, 0x01, 0x68, 0x30, 0x9C, 0x00, 0x00], is_extended_id=False)
    # while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 04 10 10 10 10 10 10 10":
    #    print(kin_socketcan.decode_frame(msg))

    # print("code data size received")
    # print("ready to start sending hex")
    # # start reading and writing the binary file here
    

    # hexUtil = HexUtility()
    # hexUtil.open_file("hex_file_copies/2.27_copy.hex")
    # write_ids = [0x04F, 0x050, 0x051, 0x052]

    # finish_write = False
    # i = 0
    # while not finish_write:
    #     data = hexUtil.get_next_data_8()
    #     if data == -1:
    #         finish_write = True

    #     packet = make_socketcan_packet(write_ids[i],data)
    #     print(packet)
    #     #print(kin_socketcan.decode_frame(packet))
    #     i += 1
    #     if i == len(write_ids):
    #         i = 0
        
            
    # print(make_socketcan_packet(0x04F,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x050,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x051,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x052,hexUtil.get_next_data_8()))
    
        