
# some helper functions for recreating a hex file, used solely by the decoder

# calculates a checksum of a line in a .hex file based on the intel hex formula
# line is in the form :llaaaatt[dd...dd]__ with last checksum byte absent
def hex_checksum(line):
    bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
    bytes_list_num = [int(i, 16) for i in bytes_list]
    two_compl = (256 - sum(bytes_list_num)) % 256
    return (hex(two_compl)[2:]).zfill(2)

# based on the start address, the according extended linear address may be added
def make_start_address(start_address):
    address = int(start_address, 16)
    if address > 0xFFFF: # if address is larger than max of 4 hex digits, need to do extended linear address records
        address_upper_16_bits = (address & 0xFFFF0000)>>16
        address_upper_16_bits_str = hex(address_upper_16_bits)[2:]
        address_upper_16_bits_str = address_upper_16_bits_str.zfill(4)
        hex_line = "02000004" + address_upper_16_bits_str 
        address_cs = hex_checksum(hex_line)
        return (":" + hex_line + str(address_cs) + "\n").upper()
    return # if < max address 0xFFFF then nothing needs to be added to the file

# given a line and adress, a .hex data line is created
# the address is the total address, not just the lower 16 bits, ex: 0x08008040
# the line is the raw data, ex: "AF004FC29..." as a string
def make_line(line, address):
    address = int(address, 16)
    hex_line = ""
    address_lower16 = (address & 0x0000FFFF)
    if(address_lower16 == 0): # if the lowest 16 bits are zero than need to go up a level (assume that hex doesn't start at zero)
        hex_line += make_start_address(hex(address)) # creates an extended linear address to reflect going up a level
    pre_cs = "10" + (hex(address_lower16)[2:].zfill(4)) + "00" + line # line before checksum
    return (hex_line + ":10" + (hex(address_lower16)[2:].zfill(4)) + "00" + line + str(hex_checksum(pre_cs)) + '\n').upper()