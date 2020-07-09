import re
import csv
import shutil

IAP_data_lookup = [

    ('10 10 10 10 10 10 10 10' , "\treceived 32 bytes"),
    ('88 88 88 88 88 88 88 88' , "\tstart sending bytes request"),
    ('99 99 99 99 99 99 99 99' , "\tready to receive bytes response"),
    ('[0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 5E|5F [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 00 00 00' , "\treceive reply of version request command"),
    ('02 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9A 00 00' , "\tsend code start address"),
    ('02 10 10 10 10 10 10 10' , "\treceive reply of code start address"),
    ('03 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9B 00 00' , "\tsend code checksum data"),
    ('03 10 10 10 10 10 10 10' , "\treceive reply of code checksum"),
    ('04 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9C 00 00' , "\tsend code data size"),
    ('04 10 10 10 10 10 10 10' , "\treceive reply of code checksum data"),
    ('05 10 00 00 00 90 00 00' , "\tsend end of hex file message"),
    ('05 20 20 20 20 20 20 20' , "\tcalculated checksum successfully"),
]  


#print(switch_IAP_data('01 08 5E 00 80 00 00 00'))
#print(switch_IAP_data('11 22 5E 00 80 00 00 00'))

def lookup(data, table):
    for pattern, value in table:
        if re.search(pattern, data):
            return value
    return None



def appendCSV(csvFile, textFile):
    #copy csv file instead of overwrite
    shutil.copy2(csvFile, "out.csv")

    with open(csvFile, 'r') as read_obj, open('out.csv', 'w', newline='') as write_obj, open(textFile, 'r') as txtFile:
        csvReader = csv.reader(read_obj)
        csvWriter = csv.writer(write_obj)

        for row in csvReader:
            row.append((txtFile.readline()).strip('\n'))
            row.append("")
            row.append("")
            row.append("")
            row.append("")
            row.append("")
            csvWriter.writerow(row)

            
#print(lookup('F3 08 5E 00 80 00 00 00', IAP_data_lookup))
# stri = "a a a a a"
# stri = stri.replace(" ", "-")
# print(stri)

#appendCSV('/home/geffen.cooper/vm_shared/can_logs/SC2.27-2.28_full.csv', 'translated_output/out.txt')

#expected = open("hex_file_copies/2.27_copy.hex", "r")
#actual = open(actual_file, "r")

# extract raw from expected
# data = expected.read()
# data_list = data.splitlines()
# raw_hex = ""
# for item in data_list:
#     if item[:3] == ":10":
#         item = item[9:]
#         item = item[:-2]
#         raw_hex += item
# expected_raw = open("hex_file_copies/2.27_copy_raw.txt", "w")
# expected_raw.write(raw_hex)

# write_ids = [0x04F, 0x050, 0x051, 0x052]

# i = 0
# while i in range(len(write_ids)):
#     print(write_ids[i])
#     i += 1
#     if i == len(write_ids):
#         i = 0
#         print('\n')

# # calculates the checksum of a page
# def calc_checksum(line):
#     bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
#     print(bytes_list)
#     print(len(bytes_list))
#     bytes_list_num = [int(i, 16) for i in bytes_list]
#     return sum(bytes_list_num)

# print(hex(calc_checksum("70100020018")))

import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
print(sys.path)
import HexUtility