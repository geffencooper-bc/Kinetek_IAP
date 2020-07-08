import argparse
from decoder import *
import hexutils as hexutil

if __name__ == "__main__":
    #----------------------csv test----------------
    # kin_csv = Decoder("csv")
   
    # # pass in the file to parse as a command line arg
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--csv_file", required=True)
    # args = parser.parse_args()
    # file_name = args.csv_file

    # with open(file_name, 'r') as csv_file:
    #     reader = csv.reader(csv_file)
    #     for row in reader:
    #         response = kin_csv.decode_frame(row)
    #         if response != None:
    #             print(response)
    #     print(kin_csv.hex_data)




    #----------------------socket_can test--------------------
    kin_socketcan = Decoder("socketcan")
    msg = can.Message(arbitration_id=0x048, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    while kin_socketcan.decode_frame(msg) != "0x0060 | 0x05 | 08 00 00 00 00":
        print(kin_socketcan.decode_frame(msg))

    print("entered IAP mode")
    
    msg = can.Message(arbitration_id=0x048, data=[0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88], is_extended_id=False)
    while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 99 99 99 99 99 99 99 99":
        print(kin_socketcan.decode_frame(msg))

    print("can start sending bytes")

    msg = can.Message(arbitration_id=0x048, data=[0x02, 0x08, 0x00, 0x80, 0x00, 0x9A, 0x00, 0x00], is_extended_id=False)
    while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 02 10 10 10 10 10 10 10":
        print(kin_socketcan.decode_frame(msg))
    
    print("start address received")

    msg = can.Message(arbitration_id=0x048, data=[0x03, 0x00, 0x87, 0x47, 0xFE, 0x9B, 0x00, 0x00], is_extended_id=False)
    while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 03 10 10 10 10 10 10 10":
       print(kin_socketcan.decode_frame(msg))

    print("checksum data received")

    msg = can.Message(arbitration_id=0x048, data=[0x04, 0x00, 0x01, 0x68, 0x30, 0x9C, 0x00, 0x00], is_extended_id=False)
    while kin_socketcan.decode_frame(msg) != "0x0069 | 0x08 | 04 10 10 10 10 10 10 10":
       print(kin_socketcan.decode_frame(msg))

    print("code data size received")
    print("ready to start sending hex")
    # start readnig and writing the binary file here

    hex_file = open("hex_file_copies/2.27_copy.hex", "r")
    print(hexutil.hex_to_raw(hex_file.readline()))
    print(hexutil.hex_to_raw(hex_file.readline()))
    print(kin_socketcan.hex_data)