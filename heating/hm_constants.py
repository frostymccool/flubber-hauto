#
# Neil Trimboy 2011
#


# Protocol for each controller
HMV2_ID = 2
HMV3_ID = 3

#
# HM Version 3 Magic Numbers
#

# Master must be in range [0x81,0xa0] = [129,160]
MASTER_ADDR_MIN = 0x81
MASTER_ADDR_MAX = 0xa0

# Define magic numbers used in messages
FUNC_READ  = 0
FUNC_WRITE = 1

BROADCAST_ADDR = 0xff
RW_LENGTH_ALL = 0xffff

KEY_LOCK_ADDR = 22
HOL_HOURS_LO_ADDR = 24
HOL_HOURS_HI_ADDR = 25
CUR_TIME_ADDR = 43

KEY_LOCK_UNLOCK = 0
KEY_LOCK_LOCK = 1

#
# HM Version 2 Magic Numbers
#
# TODO