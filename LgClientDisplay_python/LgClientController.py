import threading
from PyQt5 import QtWidgets, QtCore
import cv2
from LgClientModel import LgClientModel
from LgClientDisplay import LgClientDisplay
import queue

from TcpSendReceiver import TcpSendReceiver
from VideoRecorder import VideoRecorder
from constant.DisplayConstant import BUTTON_CV_AREA1_OBJECT_NAME, BUTTON_CV_AREA2_OBJECT_NAME, BUTTON_CV_AREA_MAX_OBJECT_NAME, BUTTON_CV_AREA_MIN_OBJECT_NAME,\
                                    BUTTON_CV_THRESHOLD_OBJECT_NAME, BUTTON_TF_DY_MV_OFF_OBJECT_NAME, BUTTON_TF_DY_MV_ON_OBJECT_NAME, BUTTON_TF_EPSILON_OBJECT_NAME, \
                                    BUTTON_TF_T1_OBJECT_NAME, BUTTON_TF_BOX_OBJECT_NAME, HIT_TEXT, KEY_DOWN_1, KEY_DOWN_2, KEY_FIRE_1, KEY_FIRE_2, KEY_LEFT_1, KEY_LEFT_2, \
                                    KEY_RIGHT_1, KEY_RIGHT_2, KEY_UP_1, KEY_UP_2, MISS_TEXT, SERVER_MESSAGE_TYPE_ALERT, SERVER_MESSAGE_TYPE_ERROR, SERVER_MESSAGE_TYPE_TITLE, \
                                    SUB_STATE_ARMED, SUB_STATE_CALIB_OFF, SUB_STATE_CALIB_ON, SUB_STATE_FIRING, SUB_STATE_LASER_OFF, SUB_STATE_LASER_ON
from constant.NetworkConfig import  REMOTE_PORT_NUM, NETWORK_CONNECTED, NETWORK_CONNECTING, NETWORK_DISCONNECTED
from constant.SettingConstant import ARMED, CALIB_ON, CMD_USE_OPENCV, CMD_USE_TF, CONFIG_ID_CV_AREA1, CONFIG_ID_CV_AREA2, CONFIG_ID_CV_AREA_MAX, CONFIG_ID_CV_AREA_MIN, \
                                    CONFIG_ID_CV_THRESHOLD, CONFIG_ID_TF_DY_MV, CONFIG_ID_TF_EPSILON, CONFIG_ID_TF_T1, CONFIG_ID_TF_T2, FIRING, LASER_ON, PRE_ARM_CODE, \
                                    SYSTEM_MODE_ARMED_MANUAL, SYSTEM_MODE_AUTO_ENGAGE, SYSTEM_MODE_LIST, SYSTEM_MODE_PRE_ARM, SYSTEM_MODE_SAFE, \
                                    SYSTEM_MODE_TEXT_ARMED_MANUAL, SYSTEM_MODE_TEXT_AUTO_ENGAGE, SYSTEM_MODE_TEXT_PRE_ARM, SYSTEM_MODE_TEXT_SAFE, SYSTEM_MODE_TEXT_UNKNOWN, \
                                    SYSTEM_MODE_UNKNOWN, AUTO_ENGAGE_PAUSE, AUTO_ENGAGE_RESUME, AUTO_ENGAGE_STOP, DEC_X, DEC_Y, FIRE_START, FIRE_STOP, INC_X, INC_Y, \
                                    PAN_DOWN_START, PAN_DOWN_STOP, PAN_LEFT_START, PAN_LEFT_STOP, PAN_RIGHT_START, PAN_RIGHT_STOP, PAN_UP_START, PAN_UP_STOP, TITLE_OPEN_CV, \
                                    TITLE_TENSOR_FLOW
                                        
class LgClientController(QtCore.QThread):

    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication([])
        self.model = LgClientModel()
        self.ui = LgClientDisplay(self.model)
        self.event_queue = queue.Queue()
        self.videoRecorder = VideoRecorder(self.update_video_file_name)
        self.videoRecorder.start()
        self.image_height = 0
        self.image_width = 0

        self.ui.pushButton_connection.clicked.connect(self.enqueue_connect_to_server)
        # State button
        self.ui.pushButton_safe_mode.clicked.connect(self.enqueue_set_safe_code)
        self.ui.pushButton_pre_arm_mode.clicked.connect(self.enqueue_set_pre_arm_code)
        self.ui.pushButton_armed_manual.clicked.connect(self.enqueue_set_armed_manual)
        self.ui.pushButton_auto_start.clicked.connect(self.enqueue_set_auto_engage_start)
        self.ui.pushButton_auto_stop.clicked.connect(self.enqueue_set_auto_engage_stop)
        
        # State
        self.stateDict = {SYSTEM_MODE_UNKNOWN:SYSTEM_MODE_TEXT_UNKNOWN,
                          SYSTEM_MODE_SAFE:SYSTEM_MODE_TEXT_SAFE,
                          SYSTEM_MODE_PRE_ARM:SYSTEM_MODE_TEXT_PRE_ARM,
                          SYSTEM_MODE_AUTO_ENGAGE:SYSTEM_MODE_TEXT_AUTO_ENGAGE,
                          SYSTEM_MODE_ARMED_MANUAL:SYSTEM_MODE_TEXT_ARMED_MANUAL
                         }
        
        # Sub state
        self.subStateDict = {ARMED:SUB_STATE_ARMED,
                             FIRING:SUB_STATE_FIRING,
                             LASER_ON:SUB_STATE_LASER_ON,
                             CALIB_ON:SUB_STATE_CALIB_ON,
                            }
        
        # Control button
        self.ui.checkbox_laser.stateChanged.connect(self.enqueue_set_laser)
        self.ui.checkbox_cal.stateChanged.connect(self.enqueue_set_calibrate)
        self.model.key_pressed_signal.connect(self.enqueue_set_key_event)
        self.ui.pushButton_algo_cv.clicked.connect(self.enqueue_set_open_cv)
        self.ui.pushButton_algo_tf.clicked.connect(self.enqueue_set_tf)
        self.ui.config_dialog.button_set_cv_threshold.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_cv_area1.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_cv_area2.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_cv_area_min.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_cv_area_max.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_tf_score.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_tf_box.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_set_tf_epsilon.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_dy_mv_on.clicked.connect(self.enqueue_set_config)
        self.ui.config_dialog.button_dy_mv_off.clicked.connect(self.enqueue_set_config)
        self.model.record_video_signal.connect(self.set_video_record)
        self.model.hit_number_siganl.connect(self.ui.hit_number)
        for key, button in self.ui.keys:
            button.clicked.connect(lambda checked, obj_name=button.objectName(): self.enqueue_set_click_event(obj_name))

        self.set_ui_update_signal()
        self.ui.show()
        self.start()

        self.app.exec_()
        self.event_queue.put(None)
        self.wait()

    def set_ui_update_signal(self):
        self.model.log_messages_signal.connect(self.ui.update_log)
        self.model.connection_state_signal.connect(self.ui.connection_state_changed)
        self.model.system_state_signal.connect(self.ui.system_state_changed)
        self.model.laser_state_signal.connect(self.ui.update_laser_state)
        self.model.calibrate_state_signal.connect(self.ui.update_calibrate_state)
        self.model.process_image_signal.connect(self.ui.display_image)
        self.model.algorithm_select_signal.connect(self.ui.update_algorithm)
        self.model.robot_action_signal.connect(self.ui.update_robot_action)
        self.model.display_alert_signal.connect(self.ui.display_alert)

    def run(self):
        while True:
            event = self.event_queue.get()
            if event is None:
                break
            func, args = event
            func(*args)
            self.event_queue.task_done()
    
    # Video Record
    def set_video_record(self, record):
        recorderState = self.videoRecorder.get_recording()
        if recorderState == record:
            return
        
        self.videoRecorder.set_recording(record, (self.image_width, self.image_height))
        if not record:
            self.videoRecorder.enqueue_stop_record_video()
    
    # Queue Function
    def enqueue_connect_to_server(self):
        connectionState = self.model.get_connection_state()
        if connectionState != NETWORK_DISCONNECTED:
            if hasattr(self, 'tcpSendReceive'):
                self.tcpSendReceive.disconnect()
            self.update_connection(NETWORK_DISCONNECTED)
        else:
            self.event_queue.put((self.connect_to_server, [connectionState]))

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
        self.event_queue.put((self.set_calibrate_state, [state]))
        
    def enqueue_set_auto_engage_start(self):
        self.event_queue.put((self.set_auto_engage_start, []))
        
    def enqueue_set_auto_engage_stop(self):
        self.event_queue.put((self.set_auto_engage_stop, []))
        
    def enqueue_set_click_event(self, object_name):
        self.event_queue.put((self.set_click_event, [object_name]))
    
    def enqueue_set_open_cv(self):
        self.event_queue.put((self.set_algorithm, [CMD_USE_OPENCV]))

    def enqueue_set_tf(self):
        self.event_queue.put((self.set_algorithm, [CMD_USE_TF]))
    
    def enqueue_set_config(self):
        sender = self.sender()
        objectName = sender.objectName()
        if objectName == BUTTON_CV_THRESHOLD_OBJECT_NAME:
            type = CONFIG_ID_CV_THRESHOLD
            value = self.ui.config_dialog.editText_open_cv_threshold.text()
        elif objectName == BUTTON_CV_AREA1_OBJECT_NAME:
            type = CONFIG_ID_CV_AREA1
            value = self.ui.config_dialog.editText_open_cv_area1.text()
        elif objectName == BUTTON_CV_AREA2_OBJECT_NAME:
            type = CONFIG_ID_CV_AREA2
            value = self.ui.config_dialog.editText_open_cv_area2.text()
        elif objectName == BUTTON_CV_AREA_MIN_OBJECT_NAME:
            type = CONFIG_ID_CV_AREA_MIN
            value = self.ui.config_dialog.editText_open_cv_area_min.text()
        elif objectName == BUTTON_CV_AREA_MAX_OBJECT_NAME:
            type = CONFIG_ID_CV_AREA_MAX
            value = self.ui.config_dialog.editText_open_cv_area_max.text()
        elif objectName == BUTTON_TF_T1_OBJECT_NAME:
            type = CONFIG_ID_TF_T1
            value = self.ui.config_dialog.editText_tf_score.text()
        elif objectName == BUTTON_TF_BOX_OBJECT_NAME:
            type = CONFIG_ID_TF_T2
            value = self.ui.config_dialog.editText_tf_box.text()
        elif objectName == BUTTON_TF_EPSILON_OBJECT_NAME:
            type = CONFIG_ID_TF_EPSILON
            value = self.ui.config_dialog.editText_tf_epsilon.text()
        elif objectName == BUTTON_TF_DY_MV_ON_OBJECT_NAME:
            type = CONFIG_ID_TF_DY_MV
            value = 1
        elif objectName == BUTTON_TF_DY_MV_OFF_OBJECT_NAME:
            type = CONFIG_ID_TF_DY_MV
            value = 0
            
        if value == "":
            return
        
        self.event_queue.put((self.set_config_value, [type, value]))

    def connect_to_server(self, connectionState):
        if connectionState == NETWORK_DISCONNECTED:
            self.update_connection(NETWORK_CONNECTING)
            remote_address = self.ui.editText_remote_address.text()
            self.model.set_remote_address(remote_address)
            self.model.add_log_message_normal(f"Connecting to {remote_address}...")
            self.tcpSendReceive = TcpSendReceiver(remote_address, 
                                                  REMOTE_PORT_NUM,
                                                  self.update_connection,
                                                  self.update_image,
                                                  self.update_text,
                                                  self.update_state,
                                                  self.update_algo)
            self.tcpSendReceive.connect()
            #TEST
            # self.model.set_connection_state(NETWORK_CONNECTED)
            # self.model.set_system_state(SYSTEM_MODE_SAFE)

    def set_safe_mode(self):
        self.model.add_log_message_emphasis("System setting to the Safe-mode.")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_SAFE)
        #TEST
        # self.update_state(SYSTEM_MODE_SAFE)

    def set_pre_arm_code(self):
        if self.model.get_system_state()&SYSTEM_MODE_PRE_ARM:
            self.update_state(SYSTEM_MODE_PRE_ARM)
        if self.model.get_pre_arm_code() == PRE_ARM_CODE:
            self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_PRE_ARM)
            return
        self.model.add_log_message_emphasis("Send Pre-arm code")
        preArmCode = self.ui.editText_pre_arm_code.text()
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
        currentState = self.model.get_system_state()
        if currentState&SYSTEM_MODE_ARMED_MANUAL:
            self.model.add_log_message_normal("laser : " + ("enabled" if state == QtCore.Qt.Checked else "disabled"))
            mergedState = (currentState|LASER_ON) if state == QtCore.Qt.Checked else (currentState&~LASER_ON)
            self.tcpSendReceive.send_state_change_request_to_server(mergedState)
        #Test
            # self.update_state(mergedState)

    def set_calibrate_state(self, state):
        currentState = self.model.get_system_state()
        if currentState&SYSTEM_MODE_ARMED_MANUAL:
            self.model.add_log_message_normal("calibrate : " + ("enabled" if state == QtCore.Qt.Checked else "disabled"))
            mergedState = (currentState|CALIB_ON) if state == QtCore.Qt.Checked else (currentState&~CALIB_ON)
            self.tcpSendReceive.send_state_change_request_to_server(mergedState)
        #Test
            # self.update_state(mergedState)

    def set_key_event(self, key, pressed):
        currentState = self.model.get_system_state()
        calChecked = self.ui.checkbox_cal.isChecked()
        if (currentState&SYSTEM_MODE_PRE_ARM):
            self.handleKeyForPreArmState(key, pressed)
        elif (currentState&SYSTEM_MODE_ARMED_MANUAL) and calChecked == False:
            self.handleKeyForManualState(key, pressed)
        elif (currentState&SYSTEM_MODE_ARMED_MANUAL) and calChecked == True:
            self.handleKeyForCalibrate(key, pressed)
    
    def set_auto_engage_start(self):
        if self.model.get_system_state()&SYSTEM_MODE_AUTO_ENGAGE:
            if self.ui.pushButton_auto_start.isChecked():
                self.model.add_log_message_normal("Resume Auto Engage mode")
                self.tcpSendReceive.send_command_to_server(AUTO_ENGAGE_RESUME)
            else:
                self.model.add_log_message_normal("Pause Auto Engage mode")
                self.tcpSendReceive.send_command_to_server(AUTO_ENGAGE_PAUSE)
            return
        
        targetOrder = self.ui.editText_target_order.text()
        if targetOrder == "":
            self.model.add_log_message_error("Empty Target")
            return
        self.model.set_target_order(targetOrder)
        self.model.add_log_message_emphasis("Target order : " + targetOrder)
        self.tcpSendReceive.send_target_order_to_server(targetOrder)
        
        self.model.add_log_message_emphasis("System setting to the Auto Engage Mode.")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_AUTO_ENGAGE)
        #Test
        # self.update_state(SYSTEM_MODE_AUTO_ENGAGE)

    def set_auto_engage_stop(self):
        self.model.add_log_message_normal("Stop Auto Engage mode")
        self.tcpSendReceive.send_state_change_request_to_server(SYSTEM_MODE_PRE_ARM)
        #Test
        # self.update_state(SYSTEM_MODE_PRE_ARM)
        
    def set_config_value(self, type, value):
        self.model.add_log_message_normal(f"Set {type}: {value}")
        self.tcpSendReceive.send_config_to_server(type, value)
    
    # Callback functions
    def update_connection(self, status):
        if self.model.get_connection_state == status:
            return
        if status == NETWORK_CONNECTED:
            self.model.set_connection_state(NETWORK_CONNECTED)
            self.model.add_log_message_normal("Connection Successful")
        elif status == NETWORK_DISCONNECTED:
            self.model.set_connection_state(NETWORK_DISCONNECTED)
            self.model.add_log_message_error("Server Disconnected")
        else:
            self.model.set_connection_state(NETWORK_CONNECTING)
    
    def update_state(self, state):
        currentState = self.model.get_system_state()
        if currentState == state and currentState&SYSTEM_MODE_PRE_ARM == 0:
            return
        if state != SYSTEM_MODE_UNKNOWN:
            stateText = self.stateDict[self.extract_system_mode(state)]
            self.model.add_log_message_server(f"[Mode] {stateText}")
        if state&SYSTEM_MODE_SAFE or state&SYSTEM_MODE_UNKNOWN:
            self.model.set_pre_arm_code("")
        self.model.set_system_state(state)
        self.handle_sub_state(currentState, state)
    
    def update_text(self, text):
        if text.find(SERVER_MESSAGE_TYPE_TITLE) != -1:
            strValue = text.replace(SERVER_MESSAGE_TYPE_TITLE, "")
            self.model.set_robot_action(strValue)
        elif text.find(SERVER_MESSAGE_TYPE_ERROR) != -1:
            strValue = text.replace(SERVER_MESSAGE_TYPE_ERROR, "")
            self.model.add_log_message_server_error(strValue)
        elif text.find(SERVER_MESSAGE_TYPE_ALERT) != -1:
            strValue = text.replace(SERVER_MESSAGE_TYPE_ALERT, "")
            self.model.set_alert(strValue)
        else:
            self.model.add_log_message_server(f"{text}")
        if text.find(HIT_TEXT) != -1 or text.find(MISS_TEXT) != -1:
            last_char = None
            for char in reversed(text):
                if char != "\n":
                    last_char = char
                    break
            if not last_char:
                return
            
            textJoin = "".join(text.split()).replace('\0','')
            last_char = textJoin[-1]
            hit_number = int(last_char)
            self.model.set_hit_number(hit_number)
        
    def update_image(self, image):
        height, width, channels = image.shape
        self.image_width = width
        self.image_height = height
        self.model.process_image_signal.emit(image)
        if self.videoRecorder.get_recording():
            self.videoRecorder.enqueue_record_video(image)
    
    def update_algo(self, algo):
        self.model.set_algo(algo)
        
    def update_video_file_name(self, fileName):
        self.model.add_log_message_normal(f"Video saved : {fileName}")
        
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
    
    def set_click_event(self, objectName):
        calChecked = self.ui.checkbox_cal.isChecked()
        if calChecked:
            if objectName == KEY_UP_1:
                startcode = INC_Y
            elif objectName == KEY_LEFT_1:
                startcode = DEC_X
            elif objectName == KEY_RIGHT_1:
                startcode = INC_X
            elif objectName == KEY_DOWN_1:
                startcode = DEC_Y
            else:
                return
            self.tcpSendReceive.send_calib_to_server(startcode)
        else:
            if objectName == KEY_UP_1:
                startcode = PAN_UP_START
                endcod = PAN_UP_STOP
            elif objectName == KEY_LEFT_1:
                startcode = PAN_LEFT_START
                endcod = PAN_LEFT_STOP
            elif objectName == KEY_RIGHT_1:
                startcode = PAN_RIGHT_START
                endcod = PAN_RIGHT_STOP
            elif objectName == KEY_DOWN_1:
                startcode = PAN_DOWN_START
                endcod = PAN_DOWN_STOP
            elif objectName == KEY_FIRE_1:
                startcode = FIRE_START
                endcod = FIRE_STOP
            else:
                return
            self.tcpSendReceive.send_command_to_server(startcode)
            self.tcpSendReceive.send_command_to_server(endcod)
    
    def handle_sub_state(self, currentState, state):
        for subState, text in self.subStateDict.items():
            if state&subState:
                self.model.add_log_message_server(f"[Action] {text}")
                if subState == LASER_ON:
                    self.model.set_laser_state(True)
                elif subState == CALIB_ON:
                    self.model.set_calibrate_state(True)
            else:
                if currentState&LASER_ON and subState == LASER_ON:
                    self.model.add_log_message_server(f"[Action] {SUB_STATE_LASER_OFF}")
                    self.model.set_laser_state(False)   
                elif currentState&CALIB_ON and subState == CALIB_ON:
                    self.model.add_log_message_server(f"[Action] {SUB_STATE_CALIB_OFF}")
                    self.model.set_calibrate_state(False)
        
    def set_algorithm(self, algo):
        if self.model.get_system_state()&SYSTEM_MODE_SAFE:
            self.tcpSendReceive.send_command_to_server(algo)
            if algo == CMD_USE_OPENCV:
                self.model.add_log_message_normal(f'Set Algorithm : {TITLE_OPEN_CV}')
            else:
                self.model.add_log_message_normal(f'Set Algorithm : {TITLE_TENSOR_FLOW}')
    
    def extract_system_mode(self, state):
        for mode in SYSTEM_MODE_LIST:
            if state & mode:
                return mode
        return SYSTEM_MODE_UNKNOWN
    
if __name__ == "__main__":
    LgClientController()