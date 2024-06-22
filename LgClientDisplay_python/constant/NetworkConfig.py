REMOTE_PORT_NUM = 5000

# Send Type
MT_COMMANDS = 1
MT_TARGET_SEQUENCE = 2
MT_PREARM = 5
MT_STATE_CHANGE_REQ = 7
MT_CALIB_COMMANDS = 8

# Receive Type
MT_IMAGE = 3
MT_TEXT = 4
MT_STATE = 6

PAN_LEFT_START = 0x01
PAN_RIGHT_START = 0x02
PAN_UP_START = 0x04
PAN_DOWN_START= 0x08
FIRE_START = 0x10
PAN_LEFT_STOP = 0xFE
PAN_RIGHT_STOP = 0xFD
PAN_UP_STOP = 0xFB
PAN_DOWN_STOP = 0xF7
FIRE_STOP = 0xEF

DEC_X = 0x01
INC_X = 0x02
DEC_Y = 0x04
INC_Y = 0x08

AUTO_ENGAGE_STOP = 17
AUTO_ENGAGE_PAUSE = 18
AUTO_ENGAGE_RESUME = 19