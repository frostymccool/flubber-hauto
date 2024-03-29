#
# Original: Neil Trimboy 2011
# Updated for Shawpad configuration: Ian Shaw
#

from hm_constants import *
import serial

# Master Address
MY_MASTER_ADDR = 0x81

# Port
S_PORT_NAME = '/dev/ttyUSB0'
COM_PORT = S_PORT_NAME
COM_BAUD = 4800
COM_SIZE = serial.EIGHTBITS
COM_PARITY = serial.PARITY_NONE
COM_STOP = serial.STOPBITS_ONE
COM_TIMEOUT = 3

# A list of controllers
# Adjust the number of rows in this list as required
# Items in each row are :
# Controller Address, ShortName, LongName, Controller Type, Graph Colour, xAP_Instance, xAP UID, T-Stat available bool, COSM ID
StatList = [
[1,  "Kit", "Kitchen",    HMV3_ID, "A020F0", "kitchen.temp", "F4061102", 1, 4],
[2,  "Brk", "Breakfast Bar", HMV3_ID, "D02090", "breakfastbar.temp", "F4061103", 1, 5],
[5,  "Din", "Dining",   HMV3_ID, "FF4500", "dining.temp","F4061104", 1, 2],
#[6,  "Liv", "Living",   HMV3_ID, "FF8C00", "living.temp", "F4061105", 0, 10],
#[7,  "Sit", "Sitting",   HMV3_ID, "FF8C00", "sitting.temp","F4061106", 0, 13],
#[8,  "Play", "Playroom",   HMV3_ID, "32CD32", "playroom.temp","F4061107", 0, 9],
[3,  "Bed1", "Our Bedroom", HMV3_ID, "FFD700", "bedroom1.temp","F4061108", 1, 2],
[4,  "Ens1", "Our Ensuite",    HMV3_ID, "6B8E23", "ensuite1.temp", "F4061109", 1, 3],
#[9, "Bed2", "Chloe's Bedroom", HMV3_ID, "1E90FF", "bedroom2.temp","F4061110", 0, 7],
[10, "Bed3", "Ethan's Bedroom", HMV3_ID, "6A5ACD", "bedroom3.temp","F4061111", 1, 8],
#[11, "Bed4", "Loft Room",  HMV3_ID, "00FA9A", "bedroom4.temp","F4061112", 0, 11],
#[12, "Ens4", "Ensuite Loft",  HMV3_ID, "00FA9A", "ensuite4.temp","F4061113", 0, 0],
#[13, "Study", "Study",  HMV3_ID, "00FA9A", "study.temp", "F4061114", 0, 12],
#[14,  "Bath", "Bathroom", HMV3_ID, "D2691E", "bathroom.temp","F4061115", 0, 0],
#[15, "BTow", "Bathroom Towel",  HMV3_ID, "00FA9A", "bathtowel.temp","F4061116", 0, 0],
#[16, "Lob", "Lobby",  HMV3_ID, "00FA9A", "lobby.temp","F4061117", 0, 0],
#[17, "Clk", "Cloak Room",  HMV3_ID, "00FA9A", "cloakroom.temp","F4061118", 0, 0],
#[18, "Dry", "Drying Rail",  HMV3_ID, "00FA9A", "drying.temp","F4061119", 0, 0],
#[19, "Hall", "Hallway",  HMV3_ID, "00FA9A", "hallway.temp","F4061120", 0 0],
]

# Named indexing into StatList
SL_ADDR = 0
SL_SHRT_NAME = 1
SL_LONG_NAME = 2
SL_CONTR_TYPE = 3
SL_GRAPH_COL = 4
SL_XAP_INSTANCE = 5
SL_XAP_UID = 6
SL_STAT_PRESENT = 7
SL_COSM_ID = 8
