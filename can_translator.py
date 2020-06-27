import csv

INDEX = 0
SYSTEM_TIME = 1
TIME_STAMP = 2
CHANNEL = 3
DIRECTION = 4
FRAME_ID = 5
TYPE = 6
FORMAT = 7
DLC = 8
DATA = 9

def switch(arg):
    # if arg == "0x0040":
    #     print ("heart beat")
    return{
        '0x0000' : "CP-->MMC   HEART_BEAT",
        '0x0001' : "CP-->MMC   CONTROLLER_CHANGE_REQUEST",
        '0x03C9' : "UNKNOWN",
        '0x0040' : "KCH-->MMC  HEART_BEAT",
        '0x04CA' : "UNKNOWN",
        '0x0060' : "NOT_USED",
        '0x0080' : "MMC-->CP   HEART_BEAT\n",
        '0x0081' : "MMC-->CP   CONTROLLER_CHANGE_VERIFICATION",
        '0x0082' : "MMC-->CP   HOUR_METER_RESPONSE"
    }.get(arg)

print(switch('0x0001'))
with open('sampleLog.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(switch(row[FRAME_ID]))