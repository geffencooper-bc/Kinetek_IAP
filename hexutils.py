# some helper functions for working with hex files

def hex_to_raw(line):
    return line[9:-3]

def hex_checksum(line):
    bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
    bytes_list_num = [int(i, 16) for i in bytes_list]
    two_compl = (256 - sum(bytes_list_num)) % 256
    return (hex(two_compl)[2:]).zfill(2)

def make_start_address(start_address):
    address = int(start_address, 16)
    if address > 0xFFFF: # if address is larger than max of 4 hex digits, need to do extended linear address records
        address_upper_16_bits = (address & 0xFFFF0000)>>16
        address_upper_16_bits_str = hex(address_upper_16_bits)[2:]
        address_upper_16_bits_str = address_upper_16_bits_str.zfill(4)
        hex_line = "02000004" + address_upper_16_bits_str 
        address_cs = hex_checksum(hex_line)
        return ":" + hex_line + str(address_cs) + "\n"
    return

def make_line(line, address):
    address = int(address, 16)
    hex_line = ""
    address_lower16 = (address & 0x0000FFFF)
    if(address_lower16 == 0): # went up a level because passed FFF0
        hex_line += make_start_address(hex(address))
    pre_cs = "10" + (hex(address_lower16)[2:].zfill(4)) + "00" + line
    return hex_line + ":10" + (hex(address_lower16)[2:].zfill(4)) + "00" + line + str(hex_checksum(pre_cs)) + '\n'