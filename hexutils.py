# some helper functions for working with hex files

def hex_checksum(line):
    bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
    bytes_list_num = [int(i, 16) for i in bytes_list]
    two_compl = 256 - sum(bytes_list_num) % 256
    return hex(two_compl)[2:]

def make_start_address(start_address):
    address = int(start_address, 16)
    if address > 0xFFFF: # if address is larger than max of 4 hex digits, need to do extended linear address records
        
        address_upper_16_bits = (address & 0xFFFF0000)>>16
        print(hex(address_upper_16_bits))
        address_upper_16_bits_str = hex(address_upper_16_bits)[2:]
        address_upper_16_bits_str = address_upper_16_bits_str.zfill(4)
        hex_line = "02000004" + address_upper_16_bits_str 
        address_cs = hex_checksum(hex_line)
        print(hex_line)
        return ":" + hex_line + str(address_cs)

print(make_start_address("01238000"))