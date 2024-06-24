from PyQt5 import QtWidgets, QtCore
import cv2
from LgClientModel import LgClientModel
from LgClientDisplay import LgClientDisplay
import queue

from TcpSendReceiver import TcpSendReceiver
from constant.DisplayConstant import KEY_DOWN_1, KEY_DOWN_2, KEY_FIRE_1, KEY_FIRE_2, KEY_LEFT_1, KEY_LEFT_2, KEY_RIGHT_1, KEY_RIGHT_2, KEY_UP_1, KEY_UP_2
from constant.NetworkConfig import AUTO_ENGAGE_PAUSE, AUTO_ENGAGE_RESUME, AUTO_ENGAGE_STOP, DEC_X, DEC_Y, FIRE_START, FIRE_STOP, INC_X, INC_Y, PAN_DOWN_START, \
                                    PAN_DOWN_STOP, PAN_LEFT_START, PAN_LEFT_STOP, PAN_RIGHT_START, PAN_RIGHT_STOP, PAN_UP_START, PAN_UP_STOP, REMOTE_PORT_NUM
from constant.SettingConstant import CALIB_ON, LASER_ON, NETWORK_CONNECTED, NETWORK_CONNECTING, NETWORK_DISCONNECTED, SYSTEM_MODE_ARMED_MANUAL, SYSTEM_MODE_AUTO_ENGAGE, \
                                    SYSTEM_MODE_PRE_ARM, SYSTEM_MODE_SAFE, SYSTEM_MODE_UNKNOWN


class LgClientController(QtCore.QThread):

    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication([])
        self.model = LgClientModel()
        self.ui = LgClientDisplay(self.model)
        self.event_queue = queue.Queue()

        self.ui.pushButton_connection.clicked.connect(self.enqueue_connect_to_server)
        # State button
        self.ui.pushButton_safe_mode.clicked.connect(self.enqueue_set_safe_code)
        self.ui.pushButton_pre_arm_mode.clicked.connect(self.enqueue_set_pre_arm_code)
        self.ui.pushButton_armed_manual.clicked.connect(self.enqueue_set_armed_manual)
        self.ui.pushButton_auto_start.clicked.connect(self.enqueue_set_auto_engage_start)
        self.ui.pushButton_auto_stop.clicked.connect(self.enqueue_set_auto_engage_stop)
        
        # Control button
        self.ui.checkbox_laser.stateChanged.connect(self.enqueue_set_laser)
        self.model.key_pressed_signal.connect(self.enqueue_set_key_event)

        self.set_ui_update_signal()
        self.ui.show()
        self.start()

        self.app.exec_()
        self.event_queue.put(None)
        self.wait()

    def set_ui_update_signal(self):
        self.model.log_messages_signal.connect(self.ui.update_log)
        self.model.robot_connected_signal.connect(self.ui.connection_state_changed)
        self.model.system_state_signal.connect(self.ui.system_state_changed)

    def run(self):
        while True:
            event = self.event_queue.get()
            if event is None:
                break
            func, args = event
            func(*args)
            self.event_queue.task_done()
    
    # Queue Function
    def enqueue_connect_to_server(self):
        self.event_queue.put((self.connect_to_server, []))

    def enqueue_set_safe_code(self):
        self.event_queue.put((self.set_safe_mode, []))

    def enqueue_set_pre_arm_code(self):
        self.event_queue.put((self.set_pre_arm_code, []))

    def enqueue_set_armed_manual(self):
        self.event_queue.put((self.set_armed_manual, []))
        
    def enqueue_set_key_event(self, key, pressed):
        self.event_queue.put((self.set_key_event, [key, pressed]))
        
    def enqueue_set_laser(self, state):
        self.event_queue.put((self.set_laser_state, [state]))
        
    def enqueue_set_calibrate(self, state):
        self.event_queue.put((self.set_calibrate, [state]))

    def enqueue_set_auto_engage_start(self):
        self.event_queue.put((self.set_auto_engage_start, []))
        
    def enqueue_set_auto_engage_stop(self):
        self.event_queue.put((self.set_auto_engage_stop, []))

    def connect_to_server(self):
        robot_connected = self.model.get_robot_connected()
        if robot_connected == NETWORK_DISCONNECTED:
            self.update_connection(NETWORK_CONNECTING)
            remote_address = self.ui.editText_remote_address.toPlainText()
            self.model.set_remote_address(remote_address)
            self.model.add_log_message_normal(f"Connecting to {remote_address}...")
            self.tcpSendReceive = TcpSendReceiver(remote_address, 
                                                  REMOTE_PORT_NUM,
                                                  self.update_connection,
                                                  self.update_image,
                                                  self.update_text,
                                                  self.update_state)
            self.tcpSendReceive.connect()
            #TEST
            # self.model.set_robot_connected(NETWORK_CONNECTED)
            # self.model.set_system_state(SYSTEM_MODE_SAFE)
        else:
            self.tcpSendReceive.disconnect()
            self.update_connection(NETWORK_DISCONNECTED)
            #TEST
            # self.model.set_robot_connected(NETWORK_DISCONNECTED)
            # self.model.set_system_state(SYSTEM_MODE_UNKNOWN)

    def set_safe_mode(self):
        self.model.add_log_message_emphasis("System setting to the Safe-mode.")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_SAFE)
        #TEST
        # self.update_state(SYSTEM_MODE_SAFE)

    def set_pre_arm_code(self):
        self.model.add_log_message_emphasis("Send Pre-arm code")
        preArmCode = self.ui.editText_pre_arm_code.toPlainText()
        self.model.set_pre_arm_code(preArmCode)
        self.tcpSendReceive.send_prearm_code_to_server(preArmCode)
        #TEST
        # self.update_state(SYSTEM_MODE_PRE_ARM)
    
    def set_armed_manual(self):
        self.model.add_log_message_emphasis("System setting to the Armed in Manual Mode.")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_ARMED_MANUAL)
        #TEST
        # self.update_state(SYSTEM_MODE_ARMED_MANUAL)

    def set_laser_state(self, state):
        self.model.add_log_message_normal("laser : " + ("enabled" if state == QtCore.Qt.Checked else "disabled"))
        mergedState = SYSTEM_MODE_ARMED_MANUAL|LASER_ON if state == QtCore.Qt.Checked else SYSTEM_MODE_ARMED_MANUAL
        self.tcpSendReceive.send_state_change_request_to_server(mergedState)

    def set_calibrate(self, state):
        self.model.add_log_message_normal("laser : " + ("enabled" if state == QtCore.Qt.Checked else "disabled"))

    def set_key_event(self, key, pressed):
        self.model.add_log_message_normal(key + (" pressed" if pressed else " released"))
        currentState = self.model.get_system_state()
        calChecked = self.ui.checkbox_cal.isChecked()
        if currentState == SYSTEM_MODE_PRE_ARM:
            self.handleKeyForPreArmState(key, pressed)
        elif currentState == SYSTEM_MODE_ARMED_MANUAL and calChecked == False:
            self.handleKeyForManualState(key, pressed)
        elif currentState == SYSTEM_MODE_ARMED_MANUAL and calChecked == True:
            self.handleKeyForCalibrate(key, pressed)
    
    def set_auto_engage_start(self):
        if self.model.get_system_state() == SYSTEM_MODE_AUTO_ENGAGE:
            if self.ui.pushButton_auto_start.isChecked():
                self.model.add_log_message_normal("Resume Auto Engage mode")
                self.tcpSendReceive.send_command_to_server(AUTO_ENGAGE_RESUME)
            else:
                self.model.add_log_message_normal("Pause Auto Engage mode")
                self.tcpSendReceive.send_command_to_server(AUTO_ENGAGE_PAUSE)
            return
        
        targetOrder = self.ui.editText_target_order.toPlainText()
        self.model.set_target_order(targetOrder)
        self.model.add_log_message_emphasis("Target order : " + targetOrder)
        self.tcpSendReceive.send_target_order_to_server(targetOrder)
        
        self.model.add_log_message_emphasis("System setting to the Auto Engage Mode.")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_AUTO_ENGAGE)
        #Test
        # self.update_state(SYSTEM_MODE_AUTO_ENGAGE)

    def set_auto_engage_stop(self):
        self.model.add_log_message_normal("Stop Auto Engage mode")
        self.tcpSendReceive.send_command_to_server(AUTO_ENGAGE_STOP)
        #Test
        # self.update_state(SYSTEM_MODE_PRE_ARM)
        
    # Callback functions
    def update_connection(self, status):
        if status == NETWORK_CONNECTED:
            self.model.add_log_message_normal("Connection Successful")
            self.model.set_robot_connected(NETWORK_CONNECTED)
        elif status == NETWORK_DISCONNECTED:
            self.model.add_log_message_error("Server Disconnected")
            self.model.set_robot_connected(NETWORK_DISCONNECTED)
        else:
            self.model.set_robot_connected(NETWORK_CONNECTING)
    
    def update_state(self, state):
        self.model.add_log_message_server(f"[Server] State : {state}")
        self.model.set_system_state(state)
    
    def update_text(self, text):
        self.model.add_log_message_server(f"[Server] Text : {text}")
        self.model.set_text_from_server(text)
        
    def update_image(self, image):
        last_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.ui.display_image(last_image)
        
    def handleKeyForPreArmState(self, key, pressed):
        if key == KEY_UP_1 or key == KEY_UP_2:
            code = PAN_UP_START if pressed else PAN_UP_STOP
        elif key == KEY_LEFT_1 or key == KEY_LEFT_2:
            code = PAN_LEFT_START if pressed else PAN_LEFT_STOP
        elif key == KEY_RIGHT_1 or key == KEY_RIGHT_2:
            code = PAN_RIGHT_START if pressed else PAN_RIGHT_STOP
        elif key == KEY_DOWN_1 or key == KEY_DOWN_2:
            code = PAN_DOWN_START if pressed else PAN_DOWN_STOP
        else:
            return
        self.tcpSendReceive.send_command_to_server(code)
        
    def handleKeyForManualState(self, key, pressed):
        if key == KEY_UP_1 or key == KEY_UP_2:
            code = PAN_UP_START if pressed else PAN_UP_STOP
        elif key == KEY_LEFT_1 or key == KEY_LEFT_2:
            code = PAN_LEFT_START if pressed else PAN_LEFT_STOP
        elif key == KEY_RIGHT_1 or key == KEY_RIGHT_2:
            code = PAN_RIGHT_START if pressed else PAN_RIGHT_STOP
        elif key == KEY_DOWN_1 or key == KEY_DOWN_2:
            code = PAN_DOWN_START if pressed else PAN_DOWN_STOP
        elif key == KEY_FIRE_1 or key == KEY_FIRE_2:
            code = FIRE_START if pressed else FIRE_STOP
        else:
            return
        self.tcpSendReceive.send_command_to_server(code)
        
    def handleKeyForCalibrate(self, key, pressed):
        if pressed == False:
            return
        
        if key == KEY_UP_1 or key == KEY_UP_2:
            code = INC_Y
        elif key == KEY_LEFT_1 or key == KEY_LEFT_2:
            code = DEC_X
        elif key == KEY_RIGHT_1 or key == KEY_RIGHT_2:
            code = INC_X
        elif key == KEY_DOWN_1 or key == KEY_DOWN_2:
            code = DEC_Y
        else:
            return
        self.tcpSendReceive.send_calib_to_server(code)

if __name__ == "__main__":
    LgClientController()