import argparse
from decoder import *


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
                print(response)
        print(kin_csv.hex_data)




    #----------------------socket_can test--------------------
    # kin_socketcan = Decoder("socketcan")
    # msg = can.Message(arbitration_id=0x045,
    #                 data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    #                 is_extended_id=False)
    # print(kin_socketcan.decode_frame(msg))
    

