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
# Controller Address, ShortName, LongName, Controller Type, Graph Colour, xAP_Instance
StatList = [
[1,  "Kit", "Kitchen Top",    HMV3_ID, "A020F0", "kitchentop.temp"],
[2,  "Brk", "Breakfast Bar", HMV3_ID, "D02090", "breakfastbar.temp"],
[3,  "Bed1", "Our Bedroom", HMV3_ID, "FFD700", "bedroom1.temp"],
[4,  "Ens1", "Our Ensuite",    HMV3_ID, "6B8E23", "ensuite1.temp"],
#[3,  "Din", "Dining",   HMV3_ID, "FF4500"],
#[4,  "Liv", "Living",   HMV3_ID, "FF8C00"],
#[10, "Study", "Study",  HMV3_ID, "00FA9A"],
#[6,  "Bath", "Bathroom", HMV3_ID, "D2691E"],
#[9,  "Play", "Playroom",   HMV3_ID, "32CD32"],
#[11, "Chloe", "Chloe's Bedroom", HMV3_ID, "1E90FF"],
#[12, "Ethan", "Ehtan's Bedroom", HMV3_ID, "6A5ACD"],
#[10, "Loft", "Loft Room",  HMV3_ID, "00FA9A"],
#[10, "Hall", "Kids Hallway",  HMV3_ID, "00FA9A"],
]

# Named indexing into StatList
SL_ADDR = 0
SL_SHRT_NAME = 1
SL_LONG_NAME = 2
SL_CONTR_TYPE = 3
SL_GRAPH_COL = 4
SL_XAP_INSTANCE = 5
