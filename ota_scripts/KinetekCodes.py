from HexUtility import make_socketcan_packet, data_string_to_byte_list

# FW_REVISION_REQUEST = make_socketcan_packet(0x045, "00 00 00 00 00 00 00 00")
# ENTER_IAP_MODE_REQUEST = make_socketcan_packet(0x048, "00 00 00 00 00 00 00 00")
# SEND_BYTES_REQUEST = make_socketcan_packet(0x048, "88 88 88 88 88 88 88 88")
# SEND_CODE     doesnt work cuz of timestamp

def get_kinetek_can_id_code(arg):
    return{
        'FW_REVISION_REQUEST' :  '0x045',
        'IAP_REQUEST':           '0x048',
        'SEND_PACKET_1':         '0x04F',
        'SEND_PACKET_2':         '0x050',
        'SEND_PACKET_3':         '0x051',
        'SEND_PACKET_4':         '0x052',
        'RESEND_PACKET_1':       '0x053',
        'RESEND_PACKET_2':       '0x054',
        'RESEND_PACKET_3':       '0x055',
        'RESEND_PACKET_4':       '0x056'
    }.get(arg)

def get_kinetek_data_code(arg):
    return{
        "DEFAULT":              '00 00 00 00 00 00 00 00',
        "ENTER_IAP_MODE":       '00 00 00 00 00 00 00 00',
        "SEND_BYTES":           '88 88 88 88 88 88 88 88',
        "CODE_START_ADDRESS":   '02 __ __ __ __ 9A 00 00',
        "TOTAL_CHECKSUM_DATA":  '03 __ __ __ __ 9B 00 00',
        "CODE_SIZE":            '04 __ __ __ __ 9C 00 00',
        "END_OF_HEX_FILE":      '05 10 10 10 10 10 10 10',
        "CHECK_CHECK_SUM":      '06 __ __ __ __ 9D __ __',
        "PAGE_CHECKSUM_DATA":   '07 __ __ __ __ 9E __ __'
    }