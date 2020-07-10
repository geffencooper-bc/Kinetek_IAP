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

# calculates the checksum of a page
def calc_checksum(line):
    bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
    print(bytes_list)
    print(len(bytes_list))
    bytes_list_num = [int(i, 16) for i in bytes_list]
    return sum(bytes_list_num)

#print(hex(calc_checksum("5AE72DE9FE4F81EA030421F0004504F0004423F000414FF0000A009450EA050302D052EA010304D10020014603B0BDE8F08FC1F30A53C5F30A542344A3F2F3330193A0FB02B3C5F3130545F4801CC1F3130141F480180CFB023300FB083E810A930A41EA8C5143EA8853A1FB03474FEA9C2505FB03734FEA982601FB06373D05260545EA1435BBEB06016EEB0503850E920E45EA8C1542EA8812A5FB0206261E67EB00070C0D44EA0334A61947EB1350C1F313044FF000031946E5FB02014FEA033545EA1455019B4FEA0432009CA3F10C03CDE900A445EA060502932B4600F059F9A3E72DE9F04D81EA030404F0004B21F0004714464FF0000A23F0004150EA070220D054EA01021DD0C1F30A550246C1F31300C7F30A56C7F3130340F4801143F48013A6EB0508101BD64608F2FD3873EB010002D308F1010801E092185B41B8F1000F03DA00200146BDE8F08D00204FF48015064607460EE0B2EB040C73EB010C04D3121B064363EB01032F436D084FEA300092185B4150EA050CEDD152EA030012D082EA040083EA0105284303D100224FF0004308E0101B8B4102D20122002302E06FF0010253101AEB060047EB085110EB0A0041EB0B01BDE8F04D00F0DCB870B521F0004303430CD0C1F30A540026D4EB060566EB0603D417AD1AA34102DB0020014670BD001C41EB025170BD96230022114600F091B80EB5002240F23343CDE9002202931346002100F0C2F803B000BD20F00040C10DC0F3160040F400007F2901DA00207047962903DCC1F19601C840704796398840704770B5C1F30A5201F000450024C1F3130140F2FF3341F480119A4201DA002070BD40F233439A42A2F2334203DC524200F02CF800E090402C43F1D0404270BDC1F30A52C1F3130140F2FF3341F480119A4201DA0020704740F233439A42A2F2334202DC524200F011B890407047202A04DB203A00FA02F1002070479140C2F1200320FA03F3194390407047202A04DB203A21FA02F00021704721FA02F3D040C2F120029140084319467047202A06DBCB17203A41FA02F043EAE07306E041FA02F3D040C2F1200291400843194670470029A8BF7047401C490008BF20F00100704710B4B0FA80FC00FA0CF050EA010404BF10BC704749B1CCF1200421FA04F411FA0CF118BF012121430843A3EB0C01CB1D4FEA00614FEA102048BF0020BCBF10BC704700EBC35010440029A4BF10BC7047401C490008BF20F0010010BC704710B5002B08DA401C41F1000192185B411A4301D120F0010010BD2DE9FF4D934611B1B1FA81F202E0B0FA80F220329246FFF77DFF039A0746884640EA0B0011435B46084304D13846414604B0BDE8F08D114653EA020016D0CAF140025846FFF775FF04460D464FF00106584652460399FFF75DFF084300D10026344345EA")))

# import sys
# sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
# #print(sys.path)
# from HexUtility import make_socketcan_packet, data_string_to_byte_list
# f = make_socketcan_packet(0x069, data_string_to_byte_list("05 20 20 20 20 20 20 20"))
# print(f.timestamp)
# print(data_string_to_byte_list("05 20 20 20 20 20 20 20"))
# print(str(make_socketcan_packet(0x069, data_string_to_byte_list("05 20 20 20 20 20 20 20"))) + "\n" 
#       + str(make_socketcan_packet(0x069, data_string_to_byte_list("05 20 20 20 20 20 20 20"))))
import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
from HexUtility import *
from KinetekCodes import *
a = "aabbccdd"
#print("_".join(a[i:i+2] for i in range(0, len(a), 2)))

def insert_spaces(string, n):
    return " ".join(string[i:i+n] for i in range(0, len(string), n))

#print(insert_spaces(a,2))

# FW_REVISION_REQUEST = make_socketcan_packet(get_kinetek_can_id_code("FW_REVISION_REQUEST"), data_string_to_byte_list(get_kinetek_data_code("DEFAULT")))
# #print(FW_REVISION_REQUEST)

# #print(format_int(92208, 4))

# def test():
#     while True:
#         return True
# test()

def decode_socketcan_packet(frame):
    can_id = hex(frame.arbitration_id)[2:].zfill(3) # form: "060"
    data = ""
    for byte in frame.data:
        data += hex(byte)[2:].zfill(2).upper() + " " # form: "00 00 00 00 00 00 00 00"
    #simple_frame = SimpleFrame(frame.timestamp, can_id, data[:-1])
    return str(can_id + " | " + data[:-1])



table = [
 
    ('069\s\|\s10\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "RECEIVED_32__BYTES"),
    ('069\s\|\s99\s99\s99\s99\s99\s99\s99\s99' ,                                                                    "SEND_BYTES_RESPONSE"),
    ('067\s\|\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s5E|5F\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s00\s00\s00' , "FW_REVISION_REQUEST_RESPONSE"),
    ('069\s\|\s02\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "SEND_START_ADDRESS_RESPONSE"),
    ('069\s\|\s03\s10\s10\s10\s10\s10\s10\s10' ,                                                                     "SEND_CHECKSUM_DATA_RESPONSE"),
    ('069\s\|\s04\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "SEND_DATA_SIZE_RESPONSE"),
    ('069\s\|\s05\s20\s20\s20\s20\s20\s20\s20' ,                                                                    "CALCULATE_CHECKSUM_RESPONSE"),
    ('069\s\|\s07\s40\s40\s40\s40\s40\s40\s40' ,                                                                    "CALCULATE_PAGE_CHECKSUM_RESPONSE"),
    ('060\s\|\s84\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]\s[0-9A-F]',                 "calculated page checksum")
] 

def lookup2(data, table):
    for pattern, value in table:
        if re.match(pattern, data):
            return value
    return "none"

# msg = make_socketcan_packet(0x67, data_string_to_byte_list("01 08 5e 00 80 00 00 00"))
# print(decode_socketcan_packet(msg))
# if decode_socketcan_packet(msg) == "067 | 01 08 5E 00 80 00 00 00":
#     print("ya")
#     #print(lookup2("069 | 99 99 99 99 99 99 99 99", table))
#     print(lookup2(decode_socketcan_packet(msg), table))

#print(re.search('067\s\|\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s5E|5F\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s00\s00\s00', "067 | 01 08 5E 00 80 00 00 00"))
# 10 10 10 10 10 10 10 10
# 99 99 99 99 99 99 99 99
# 11 1  11 11 11 11 11 11

# def reverse_bytes(string):
#     string = string.replace(" ", "")
#     bytes_list = [string[i:i+2] for i in range(0, len(string), 2)]
#     bytes_list.reverse()
#     string = ""
#     for i in range(len(bytes_list)):
#         string += bytes_list[i] + " "
#     return string[:-1]

#print(reverse_bytes("ab cd ef gh"))

# hex_file = open("scratch.txt", "r")
# hex_lines = hex_file.readlines()

# print(hex_lines[len(hex_lines)-1][1:3])

a = [1, 2, 3, 4, 5, 6, 7, 8]
print(a)
a.clear
print(a)