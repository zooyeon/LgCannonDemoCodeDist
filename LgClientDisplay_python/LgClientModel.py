from PyQt5 import QtCore
from constant.SettingConstant import NETWORK_DISCONNECTED, SYSTEM_MODE_UNKNOWN

class LgClientModel(QtCore.QObject):
    log_messages_signal = QtCore.pyqtSignal(list)
    robot_connected_signal = QtCore.pyqtSignal(int)
    system_state_signal = QtCore.pyqtSignal(int)
    key_pressed_signal = QtCore.pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.remote_address = "raspberrypi.local"
        self.pre_arm_code = ""
        self.target_order = ""
        self.system_state = SYSTEM_MODE_UNKNOWN
        self.log_messages = []
        self.text_from_server = ""
        self.robot_connected = NETWORK_DISCONNECTED

    def set_remote_address(self, address):
        self.remote_address = address

    def get_remote_address(self):
        return self.remote_address
    
    def set_pre_arm_code(self, code):
        self.pre_arm_code = code
        
    def get_pre_arm_code(self):
        return self.pre_arm_code

    def add_log_message_normal(self, message):
        self.log_messages.append(f'<span style="color:black">{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)
    
    def add_log_message_emphasis(self, message):
        self.log_messages.append(f'<span style="color:green">{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)

    def add_log_message_error(self, message):
        self.log_messages.append(f'<span style="color:red">{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)

    def add_log_message_server(self, message):
        self.log_messages.append(f'<span style="color:blue">{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)

    def set_robot_connected(self, connected):
        self.robot_connected = connected
        self.robot_connected_signal.emit(connected)

    def get_robot_connected(self):
        return self.robot_connected
    
    def set_system_state(self, state):
        self.system_state = state
        self.system_state_signal.emit(state)
    
    def get_system_state(self):
        return self.system_state
    
    def set_target_order(self, target):
        self.target_order = target
        
    def set_text_from_server(self, text):
        self.text_from_server = text