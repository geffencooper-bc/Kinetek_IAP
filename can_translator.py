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

def switch_frame(arg):
    return{
        '0x0000' : "CP-->MMC   HEART_BEAT", 
        '0x0001' : "CP-->MMC   CONTROLLER_CHANGE_REQUEST     ",
        '0x0014' : "HT-->KT    IAP REQUEST",
        '0x0015' : "HT-->KT    IAP RESPONSE",    
        '0x03C9' : "UNKNOWN",
        '0x0040' : "KCH-->MMC  HEART_BEAT",
        '0x04CA' : "UNKNOWN",
        '0x0060' : "NOT_USED",
        '0x0080' : "MMC-->CP   HEART_BEAT\t",
        '0x0081' : "MMC-->CP   CONTROLLER_CHANGE_VERIFICATION",
        '0x0082' : "MMC-->CP   HOUR_METER_RESPONSE"
    }.get(arg)

def switch_command_data(arg):
    return{
        'F2 03' : "\tBRUSH_ENABLE = ",
        'F9 01' : "\tVACUUM_ENABLE = ",
        'F5 01' : "\tBRUSH_DECK_ENABLE = ",
        'F6 01' : "\tSQUEEGEE_ENABLE = ",
        'F7 03' : "\tVALVE_ENABLE = ",
        'F7 05' : "\tREVERSE_ALARM_ENABLE = ",
        'F7 01' : "\tAUX1_OUT_ENABLE = ",
        'F8 01' : "\tAUX2_OUT_ENABLE = ",
        'F2 04' : "\tBRUSH_UNLOAD = ",
        'F2 08' : "\tBRUSH_LOAD = ",
        'F1 04' : "\tTRACTION_DIRECTION = "
    }.get(arg)

def switch_command_data2(arg):
    return{
        'F1 00' : "\tTRACTION_SPEED_HIGH",
        'F1 01' : "\tTRACTION_SPEED_MEDIUM",
        'F1 02' : "\tTRACTION_SPEED_LOW",
        'F2 00' : "\tBRUSH_SPEED_HIGH",
        'F2 01' : "\tBRUSH_SPEED_MEDIUM",
        'F2 02' : "\tBRUSH_SPEED_LOW",
        'F2 05' : "\tBRUSH_PRESSURE_HIGH",
        'F2 06' : "\tBRUSH_PRESSURE_MEDIUM",
        'F2 07' : "\tBRUSH_PRESSURE_LOW"
    }.get(arg)

def switch_state(arg):
    return{
        '00 00' : "OFF",
        '00 01' : "ON",
        '00 02' : "REVERSE",
    }.get(arg)

with open('/home/geffen.cooper/vm_shared/can_logs/output.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    translated_data = "\t\t\t\t\----------START OF STREAM----------\n\n"

    for row in reader:
        frm_id = str(row[FRAME_ID])
        # parse the frame id
        translated_data += '\n' + str(switch_frame(frm_id))

        # parse the command frames
        if frm_id == "0x0001" or frm_id == "0x0081":
             if str(switch_command_data(str(row[DATA])[6:11])) == "None":
                 translated_data +=  str(switch_command_data2(str(row[DATA])[6:11]))
             else:
                 translated_data +=  str(switch_command_data(str(row[DATA])[6:11])) + str(switch_state(str(row[DATA])[12:17]))
        
        # parse the KT heart beat frames
        if frm_id == "0x0080":
             translated_data +=  "page: " + str(row[DATA])[6:8] + '\n' # + "\t" + str(switch_hb_data(str(row[DATA])[10:]))

    print(translated_data)