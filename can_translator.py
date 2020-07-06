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

def switch_frame_id(arg):
    return{
        '0x0000' : "CP-->MMC   HEART_BEAT", 
        '0x0001' : "CP-->MMC   CONTROLLER_CHANGE_REQUEST     ",
        '0x0002' : "CP-->MMC   HOUR_METER_REQUEST            ",
        '0x0005' : "KCH-->MMC  SEND_VERSION_REQUEST_COMMAND  ",  
        '0x03C9' : "UNKNOWN",
        '0x0040' : "KCH-->MMC  HEART_BEAT",
        '0x0041' : "KCH-->MMC  HEART_BEAT2",
        '0x0045' : "KCH-->MMC  FW_REVISION_REQUEST",
        '0x0048' : "KCH-->MMC  IAP_REPLY_TO_LCD (IAP_REQUEST)",
        '0x004F' : "KCH-->MMC  1st 8 bytes",
        '0x0050' : "KCH-->MMC  2nd 8 bytes",
        '0x0051' : "KCH-->MMC  3rd 8 bytes",
        '0x0052' : "KCH-->MMC  4th 8 bytes",
        '0x0053' : "?-->?      FW_UNKNOWN",
        '0x0054' : "?-->?      FW_UNKNOWN",
        '0x0055' : "?-->?      FW_UNKNOWN",
        '0x0056' : "?-->?      FW_UNKNOWN",
        '0x0060' : "?-->?      NOT_USED",
        '0x0067' : "MMC-->KCH  FW_REVISION_RESPONSE",
        '0x0069' : "MMC-->KCH  HOST_IAP_REQUEST (IAP_RESPONSE)",
        '0x0080' : "MMC-->CP   **HEART_BEAT**",
        '0x0081' : "MMC-->CP   CONTROLLER_CHANGE_VERIFICATION",
        '0x0082' : "MMC-->CP   HOUR_METER_RESPONSE",
        '0x04CA' : "?-->?      CONTROL_PANEL_UPDATE_COMMAND"
    }.get(arg)

def switch_command_data(arg):
    return{
        'F1 04' : "\tTRACTION_DIRECTION = ",
        'F2 03' : "\tBRUSH_ENABLE = ",
        'F2 04' : "\tBRUSH_UNLOAD = ",
        'F2 08' : "\tBRUSH_LOAD = ",
        'F5 01' : "\tBRUSH_DECK_ENABLE = ",
        'F6 01' : "\tSQUEEGEE_ENABLE = ",
        'F7 03' : "\tVALVE_ENABLE = ",
        'F7 05' : "\tREVERSE_ALARM_ENABLE = ",
        'F7 01' : "\tAUX1_OUT_ENABLE = ",
        'F8 01' : "\tAUX2_OUT_ENABLE = ",
        'F9 01' : "\tVACUUM_ENABLE = "
        
    }.get(arg)

def switch_command_data2(arg):
    return{
        '03 27' : "\tREPROGRAM_CONFIRM",
        'F1 00' : "\tTRACTION_SPEED_HIGH",
        'F1 01' : "\tTRACTION_SPEED_MEDIUM",
        'F1 02' : "\tTRACTION_SPEED_LOW",
        'F1 06' : "\tTOP_SPEED_ADJUSTMENT",
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
        '00 02' : "REVERSE"
    }.get(arg)


def switch_IAP_data(arg):
    return{
        '03 27' : "\tEnter IAP Mode",
        '10 10 10 10 10 10 10 10' : "\treceived 32 bytes",
        '88 88 88 88 88 88 88 88' : "\tstart sending bytes request",
        '99 99 99 99 99 99 99 99' : "\tready to receive bytes response",
        '01 08 5E 00 80 00 00 00' : "\treceive reply of version request command",
        '02 08 00 80 00 9A 00 00' : "\tsend code start address",
        '02 10 10 10 10 10 10 10' : "\treceive reply of code start address",
        '03 00 87 47 FE 9B 00 00' : "\tsend code data size",
        '03 10 10 10 10 10 10 10' : "\treceive reply of code data size",
        '04 00 01 68 30 9C 00 00' : "\tsend code checksum data",
        '04 10 10 10 10 10 10 10' : "\treceive reply of code checksum data",
        '05 10 00 00 00 90 00 00' : "\tsend end of hex file message",
        '05 20 20 20 20 20 20 20' : "\tcalculated checksum successfully",
        

    }.get(arg)


# open the csv file and create the csv reader object
with open('/home/geffen.cooper/vm_shared/can_logs/boot_00.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    translated_data = ""# "\t\t\t\t\----------START OF STREAM----------\n\n"

    # parse through all rows in csv file
    for row in reader:
        frm_id = str(row[FRAME_ID])

        # parse the frame id column
        translated_data += '\n' + str(switch_frame_id(frm_id))

        # parse the command/verification frames
        if frm_id == "0x0001" or frm_id == "0x0081":
             if str(switch_command_data(str(row[DATA])[6:11])) != "None":
                 translated_data +=  str(switch_command_data(str(row[DATA])[6:11])) + str(switch_state(str(row[DATA])[12:17]))
             if str(switch_command_data2(str(row[DATA])[6:11])) != "None":
                 translated_data +=  str(switch_command_data2(str(row[DATA])[6:11]))
        if str(row[DLC]) == "0x08" and str(switch_IAP_data(str(row[DATA])[3:26])) != "None":
                 translated_data += str(switch_IAP_data(str(row[DATA])[3:26]))     
                 
        
        # parse the KT heart beat frames
        if frm_id == "0x0080":
             translated_data +=  "page: " + str(row[DATA])[6:8] # + "\t" + str(switch_hb_data(str(row[DATA])[10:]))

    print(translated_data)