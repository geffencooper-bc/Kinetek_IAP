import re

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

def lookup(s, lookups):
    for pattern, value in IAP_data_lookup:
        if re.search(pattern, s):
            return value
    return None

print(lookup('F3 08 5E 00 80 00 00 00', IAP_data_lookup))