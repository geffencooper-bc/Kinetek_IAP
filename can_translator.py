import csv
import argparse
import re

# script to parse CSV output of USB-CAN tool and interpret IAP messages
# call the script with a file location as a command line arg as follows:  '--csvFile file.csv' 

# CSV columns
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

# equivalent of a switch statement in python
def switch_frame_id(arg):
    return{        # sender           frame_id meaning
        '0x0000' : "Control Panel:    HEART_BEAT", 
        '0x0001' : "Control Panel:    CONTROLLER_CHANGE_REQUEST     ",
        '0x0002' : "Control Panel:    HOUR_METER_REQUEST",
        '0x0005' : "KC Tool:          SEND_VERSION_REQUEST_COMMAND  ",  
        '0x03C9' : "Kinetek:          BATTERY_INFO",
        '0x0040' : "BCM:              HEART_BEAT",
        '0x0041' : "BCM               AUTONOMY_CONTROL_COMMAND",
        '0x0045' : "KC Tool:          FW_REVISION_REQUEST",
        '0x0048' : "KC Tool:          IAP_REPLY_TO_LCD (IAP_REQUEST)",
        '0x004F' : "KC Tool:          1st 8 bytes",
        '0x0050' : "KC Tool:          2nd 8 bytes",
        '0x0051' : "KC Tool:          3rd 8 bytes",
        '0x0052' : "KC Tool:          4th 8 bytes",
        '0x0053' : "KC Tool:          IAP_UNKNOWN",
        '0x0054' : "KC Tool:          IAP_UNKNOWN",
        '0x0055' : "KC Tool:          IAP_UNKNOWN",
        '0x0056' : "KC Tool:          IAP_UNKNOWN",
        '0x0060' : "KC Tool:          NOT_USED",
        '0x0067' : "Kinetek:          FW_REVISION_RESPONSE           ",
        '0x0069' : "Kinetek:          HOST_IAP_REQUEST (IAP_RESPONSE)",
        '0x0080' : "Kinetek:          HEART_BEAT",
        '0x0081' : "Kinetek:          CONTROLLER_CHANGE_VERIFICATION",
        '0x0082' : "Kinetek:          HOUR_METER_RESPONSE",
        '0x04CA' : "Control Panel:    CONTROL_PANEL_UPDATE_COMMAND"
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
        '03 27' : "\tENTER_IAP_MODE",
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


# def switch_IAP_data(arg):
#     return{
#         '10 10 10 10 10 10 10 10' : "\treceived 32 bytes",
#         '88 88 88 88 88 88 88 88' : "\tstart sending bytes request",
#         '99 99 99 99 99 99 99 99' : "\tready to receive bytes response",
#         '01 08 5E 00 80 00 00 00' : "\treceive reply of version request command",
#         '02 08 00 80 00 9A 00 00' : "\tsend code start address",
#         '02 10 10 10 10 10 10 10' : "\treceive reply of code start address",
#         '03 00 87 47 FE 9B 00 00' : "\tsend code checksum data",
#         '03 10 10 10 10 10 10 10' : "\treceive reply of code checksum",
#         '04 00 01 68 30 9C 00 00' : "\tsend code data size",
#         '04 10 10 10 10 10 10 10' : "\treceive reply of code checksum data",
#         '05 10 00 00 00 90 00 00' : "\tsend end of hex file message",
#         '05 20 20 20 20 20 20 20' : "\tcalculated checksum successfully",
        

#     }.get(arg)

# use regex for IAP data because is different for each fw version
IAP_data_lookup = [

    ('10 10 10 10 10 10 10 10' ,                                                            "\treceived 32 bytes"),
    ('88 88 88 88 88 88 88 88' ,                                                            "\tstart sending bytes request"),
    ('99 99 99 99 99 99 99 99' ,                                                            "\tready to receive bytes response"),
    ('[0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 5E|5F [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 00 00 00' , "\treceive reply of version request command"),
    ('02 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9A 00 00' ,    "\tsend code start address"),
    ('02 10 10 10 10 10 10 10' ,                                                            "\treceive reply of code start address"),
    ('03 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9B 00 00' ,    "\tsend code checksum data"),
    ('03 10 10 10 10 10 10 10' ,                                                            "\treceive reply of code checksum"),
    ('04 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 9C 00 00' ,    "\tsend code data size"),
    ('04 10 10 10 10 10 10 10' ,                                                            "\treceive reply of code checksum data"),
    ('05 10 00 00 00 90 00 00' ,                                                            "\tsend end of hex file message"),
    ('05 20 20 20 20 20 20 20' ,                                                            "\tcalculated checksum successfully"),
] 

def lookup(data, table):
    for pattern, value in table:
        if re.search(pattern, data):
            return value
    return ""

def translate_frame_data(frame_id, frame_data_size, frame_data):
    translated_data = ""

    # BCM/Autonomous request or response
    if frame_id == "0x0001" or frame_id == "0x0081":
        # command type one
        if str(switch_command_data(str(frame_data)[6:11])) != "None":
            translated_data +=  str(switch_command_data(str(frame_data)[6:11])) + str(switch_state(str(frame_data)[12:17]))
        # command type two
        if str(switch_command_data2(str(frame_data)[6:11])) != "None":
            translated_data +=  str(switch_command_data2(str(frame_data)[6:11]))
    
    # IAP request or response
    if frame_id == '0x0045' or frame_id == '0x0048' or frame_id == '0x0067' or frame_id =='0x0069':
        translated_data += lookup(str(frame_data)[3:26], IAP_data_lookup)

    return translated_data



def translate_frames(fileName):
    # open the csv file and create the csv reader object
    with open(fileName, 'r') as csv_file:
        reader = csv.reader(csv_file)
        
        translated_data = ""
        # parse through all rows in csv file
        for row in reader:
            # get the frame id, data size, and data of the current row
            frame_id = str(row[FRAME_ID])
            frame_data_size = row[DLC]
            frame_data = row[DATA]

            # translate frame id
            translated_data += '\n' + str(switch_frame_id(frame_id))

            # translate frame data
            translated_data += translate_frame_data(frame_id, frame_data_size, frame_data)    
            
            # translate the Kinetek heart beat frames
            if frame_id == "0x0080":
                translated_data +=  " page: " + str(row[DATA])[6:8]

        return translated_data
    


if __name__ == "__main__":

    # pass in the file to parse as a command line arg
    parser = argparse.ArgumentParser()
    parser.add_argument("--csvFile", required=True)
    args = parser.parse_args()
    fileName = args.csvFile

    # parse the csv file
    translated_data = translate_frames(fileName)

    # append the parsed data exactly adjacent to the csv file
    output = open("translated_output/out.txt", "w")
    output.write(translated_data)
    output.close()

    