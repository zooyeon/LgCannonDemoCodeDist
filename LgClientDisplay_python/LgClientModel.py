from PyQt5 import QtCore
import numpy as np
from constant.NetworkConfig import NETWORK_DISCONNECTED
from constant.SettingConstant import SYSTEM_MODE_UNKNOWN

class LgClientModel(QtCore.QObject):
    log_messages_signal = QtCore.pyqtSignal(list)
    connection_state_signal = QtCore.pyqtSignal(int)
    system_state_signal = QtCore.pyqtSignal(int)
    laser_state_signal = QtCore.pyqtSignal(bool)
    calibrate_state_signal = QtCore.pyqtSignal(bool)
    process_image_signal = QtCore.pyqtSignal(np.ndarray)
    algorithm_select_signal = QtCore.pyqtSignal(int)
    robot_action_signal = QtCore.pyqtSignal(str)
    display_alert_signal = QtCore.pyqtSignal(str)

    key_pressed_signal = QtCore.pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.remote_address = "raspberrypi.local"
        self.pre_arm_code = ""
        self.target_order = ""
        self.system_state = SYSTEM_MODE_UNKNOWN
        self.log_messages = []
        self.connectionState = NETWORK_DISCONNECTED

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
        self.log_messages.append(f'<span style="color:blue">[Server]{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)
        
    def add_log_message_server_error(self, message):
        self.log_messages.append(f'<span style="color:red">[Server]{message}</span><br>')
        self.log_messages_signal.emit(self.log_messages)

    def set_connection_state(self, connected):
        self.connectionState = connected
        self.connection_state_signal.emit(connected)

    def get_connection_state(self):
        return self.connectionState
    
    def set_system_state(self, state):
        self.system_state = state
        self.system_state_signal.emit(state)
    
    def get_system_state(self):
        return self.system_state
    
    def set_target_order(self, target):
        self.target_order = target
        
    def set_laser_state(self, enabled):
        self.laser_state_signal.emit(enabled)
        
    def set_calibrate_state(self, enabled):
        self.calibrate_state_signal.emit(enabled)
    
    def set_image(self, image):
        self.process_image_signal.emit(image)
        
    def set_algo(self, algo):
        self.algorithm_select_signal.emit(algo)
        
    def set_robot_action(self, action):
        self.robot_action_signal.emit(action)
    
    def set_alert(self, alert):
        self.display_alert_signal.emit(alert)