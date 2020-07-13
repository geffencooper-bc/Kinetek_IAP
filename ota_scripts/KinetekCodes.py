#!/usr/bin/env python3

# this file is essentially a config file with all the kinetek command and response codes

import re


#ENTER_IAP_MODE_RESPONSE = "060 | 80 00 00 00 00"

# used for decoding requests/responses
# the left side is  a regex pattern and the right side is the decoded expected response
# the lookup function searches through this table to see if the expected response is found
IAP_data_lookup = [
    ('060\s\|\s80\s00\s00\s00\s00' ,                                                                                "IN_IAP_MODE"),
    ('081\s\|\s1D\s03\s27\s00\s00' ,                                                                                "ENTER_IAP_MODE_RESPONSE_SELECTIVE"),
    ('069\s\|\s10\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "RECEIVED_32__BYTES"),
    ('069\s\|\s99\s99\s99\s99\s99\s99\s99\s99' ,                                                                    "SEND_BYTES_RESPONSE"),
    ('067\s\|\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s5E|5F\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s00\s00\s00' , "FW_REVISION_REQUEST_RESPONSE"),
    ('069\s\|\s02\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "SEND_START_ADDRESS_RESPONSE"),
    ('069\s\|\s03\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "SEND_CHECKSUM_DATA_RESPONSE"),
    ('069\s\|\s04\s10\s10\s10\s10\s10\s10\s10' ,                                                                    "SEND_DATA_SIZE_RESPONSE"),
    ('069\s\|\s05\s20\s20\s20\s20\s20\s20\s20' ,                                                                    "END_OF_HEX_FILE_RESPONSE"),
    ('069\s\|\s06\s30\s30\s30\s30\s30\s30\s30' ,                                                                    "CALCULATE_TOTAL_CHECKSUM_RESPONSE"),
    ('069\s\|\s07\s40\s40\s40\s40\s40\s40\s40' ,                                                                    "CALCULATE_PAGE_CHECKSUM_RESPONSE"),
    ('060\s\|\s84\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]\s[0-9A-F][0-9A-F]',                         "SELF_CALCULATED_PAGE_CHECKSUM")
] 

# find the according pattern in the above table
def lookup(data, table):
    for pattern, value in table:
        if re.match(pattern, data):
            return value
    return ""

# essentially just a switch statement for can_ids
def get_kinetek_can_id_code(arg):
    return{
        'KINETEK_COMMAND':       0x001,
        'FW_REVISION_REQUEST':   0x045,
        'IAP_REQUEST':           0x048,
        'SEND_PACKET_1':         0x04F,
        'SEND_PACKET_2':         0x050,
        'SEND_PACKET_3':         0x051,
        'SEND_PACKET_4':         0x052,
        'RESEND_PACKET_1':       0x053,
        'RESEND_PACKET_2':       0x054,
        'RESEND_PACKET_3':       0x055,
        'RESEND_PACKET_4':       0x056
    }.get(arg)

# essentially just a switch statement for can_data_byets
def get_kinetek_data_code(arg):
    return{
        "DEFAULT":                       [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        "ENTER_IAP_MODE_FORCED":         [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        "ENTER_IAP_MODE_SELECTIVE":      [0x1D, 0x03, 0x27, 0x00, 0x00],
        "SEND_BYTES":                    [0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88],
        "CODE_START_ADDRESS_PREFIX":     [0x02],
        "CODE_START_ADDRESS_SUFFIX":     [0x9A, 0x00, 0x00],
        "SEND_CHECKSUM_PREFIX":          [0x03],
        "SEND_CHECKSUM_SUFFIX":          [0x9B, 0x00, 0x00],  
        "SEND_DATA_SIZE_PREFIX":         [0x04],
        "SEND_DATA_SIZE_SUFFIX":         [0x9C, 0x00, 0x00],
        "END_OF_HEX_FILE_PREFIX":        [0x05],
        "END_OF_HEX_FILE_SUFFIX":        [0x00, 0x00, 0x00, 0x90, 0x00, 0x00],
        "TOTAL_CHECKSUM_PREFIX":         [0x06],
        "TOTAL_CHECKSUM_SUFFIX":         [0x9D, 0x00, 0x00],
        "PAGE_CHECKSUM_PREFIX":          [0x07],
        "PAGE_CHECKSUM_MID":             [0x9E],
        "PAGE_CHECKSUM_SUFFIX":          [0x00]
    }.get(arg)