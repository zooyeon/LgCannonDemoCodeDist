import os
import sys
from PyQt5.QtGui import QMovie, QImage, QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets

from display.ColorLabel import ColorLabel
from display.ConfigDialog import ConfigDialog
from LgClientModel import LgClientModel
from display.NumericPlainTextEdit import NumericPlainTextEdit
import constant.DisplayConstant as Display
import constant.SettingConstant as Setting
import constant.NetworkConfig as Network
import constant.StyleSheet as Style
import keyboard

from VideoPlayer import VideoPlayer

messageBox = None

class LgClientDisplay(QtWidgets.QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.stateFuncDict = {
            Setting.SYSTEM_MODE_UNKNOWN: self.enter_unknown_mode,
            Setting.SYSTEM_MODE_SAFE: self.enter_safe_mode,
            Setting.SYSTEM_MODE_PRE_ARM: self.enter_pre_arm_mode,
            Setting.SYSTEM_MODE_ARMED_MANUAL: self.enter_armed_manual_mode,
            Setting.SYSTEM_MODE_AUTO_ENGAGE: self.enter_auto_engage_mode
        }
        self.handlers = {}
        self.setupUi(self)
        self.setup_key_event_listeners()
        self.installEventFilter(self)
        self.networkConnected = False

    def setup_key_event_listeners(self):
        self.keys = [
            (Display.KEY_UP_1, self.button_up),
            (Display.KEY_UP_2, self.button_up),
            (Display.KEY_DOWN_1, self.button_down),
            (Display.KEY_DOWN_2, self.button_down),
            (Display.KEY_LEFT_1, self.button_left),
            (Display.KEY_LEFT_2, self.button_left),
            (Display.KEY_RIGHT_1, self.button_right),
            (Display.KEY_RIGHT_2, self.button_right),
            (Display.KEY_FIRE_1, self.button_fire),
            (Display.KEY_FIRE_2, self.button_fire)
        ]
        
        for key, button in self.keys:
            self.bind_key_to_button(key, button)
            keyboard.on_press_key(key, lambda _, k=key: self.handle_key_event(k, True))
            keyboard.on_release_key(key, lambda _, k=key: self.handle_key_event(k, False))
            
    def bind_key_to_button(self, key, button):
        press_handler = keyboard.on_press_key(key, lambda _: button.setDown(True))
        release_handler = keyboard.on_release_key(key, lambda _: button.setDown(False))
        self.handlers[key] = (press_handler, release_handler)

    def unbind_key_from_button(self, key):
        if key in self.handlers:
            press_handler, release_handler = self.handlers[key]
            if press_handler in keyboard._hooks:
                try:
                    keyboard.unhook(press_handler)
                except KeyError as e:
                    print(f"Error unhooking press_handler for key {key}: {e}")
            if release_handler in keyboard._hooks:
                try:
                    keyboard.unhook(release_handler)
                except KeyError as e:
                    print(f"Error unhooking release_handler for key {key}: {e}")
            del self.handlers[key]
        else:
            print(f"No handlers found for key {key}")

    def mousePressEvent(self, event):
        if self.editText_remote_address.geometry().contains(event.pos()):
            self.editText_remote_address.setFocus()
        else:
            clicked_widget = self.childAt(event.pos())
            if clicked_widget:
                clicked_widget.setFocus()

    def setupUi(self, LgClientDisplay):
        LgClientDisplay.setObjectName(Display.WINDOW_TITLE)
        LgClientDisplay.resize(Display.WINDOW_WIDTH, Display.WINDOW_HEIGHT)
        self.setupWindow(LgClientDisplay)
        self.setupMenuBar(LgClientDisplay)
        self.setupStatusBar(LgClientDisplay)
        
        self.config_dialog = ConfigDialog(self)
        self.video_player = VideoPlayer(self.closeVideoPlayer)
        
        self.centralwidget = QtWidgets.QWidget(LgClientDisplay)
        self.centralwidget.setObjectName(Display.CENTRAL_OBJECT_NAME)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralwidget.setLayout(self.mainLayout)

        self.setupCentralWidget()

        LgClientDisplay.setCentralWidget(self.centralwidget)
        self.retranslateUi(LgClientDisplay)
        QtCore.QMetaObject.connectSlotsByName(LgClientDisplay)

    def setupWindow(self, LgClientDisplay):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LgClientDisplay.sizePolicy().hasHeightForWidth())
        LgClientDisplay.setSizePolicy(sizePolicy)
        LgClientDisplay.setMinimumSize(QtCore.QSize(Display.WINDOW_WIDTH, Display.WINDOW_HEIGHT))
        LgClientDisplay.setFont(self.getRegularFont(11))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.resource_path(Display.WINDOW_ICON_PATH)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LgClientDisplay.setWindowIcon(icon)
        LgClientDisplay.setStyleSheet(self.getGroupBoxStyle())
        LgClientDisplay.setIconSize(QtCore.QSize(Display.WINDOW_ICON_SIZE, Display.WINDOW_ICON_SIZE))

    def setupCentralWidget(self):
        self.leftLayout = QtWidgets.QVBoxLayout()
        
        self.setupSystemStatePanel()
        self.setupConnectionPanel()
        self.setupModeControlPanel()
        self.setupCommandPanel()
        self.setupLogPanel()

        self.leftLayout.addWidget(self.groupBox_system_state_panel)
        self.leftLayout.addWidget(self.groupBox_connection_panel)
        self.leftLayout.addWidget(self.groupBox_mode_control_panel)
        self.leftLayout.addWidget(self.groupBox_command_panel)
        self.leftLayout.addWidget(self.nonEditText_log)

        self.setupAlgoSelectionPanel()
        self.setupRobotActionPanel()
        self.setupRecordPlayPanel()
        self.setupCameraVideoPanel()
        self.set_record_button_enabled(False)
        
        self.algoLayout = QtWidgets.QHBoxLayout()
        self.algoLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.algoLayout.addWidget(self.groupBox_algo)
        self.algoLayout.addWidget(self.groupBox_robot_action)
        self.algoLayout.addStretch()
        self.algoLayout.addWidget(self.groupBox_record_play)
        
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.rightLayout.addLayout(self.algoLayout)
        self.rightLayout.addWidget(self.groupBox_camera_video)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addLayout(self.leftLayout)
        self.horizontalLayout.addLayout(self.rightLayout)

        self.mainLayout.addLayout(self.horizontalLayout)

    def setupMenuBar(self, LgClientDisplay):
        self.menubar = QtWidgets.QMenuBar(LgClientDisplay)
        self.menubar.setGeometry(QtCore.QRect(0, 0, Display.MENUBAR_WIDHT, Display.MENUBAR_HEIGHT))
        self.menubar.setStyleSheet(self.getMenuBarStyle())
        self.menubar.setObjectName(Display.MENUBAR_OBJECT_NAME)

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setStyleSheet(self.getMenuStyle())
        self.menuFile.setObjectName(Display.MENUFILE_OBJECT_NAME)

        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setStyleSheet(self.getMenuStyle())
        self.menuHelp.setObjectName(Display.MENUHELP_OBJECT_NAME)

        LgClientDisplay.setMenuBar(self.menubar)
        self.setupMenuActions()
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

    def setupMenuActions(self):
        self.actionExit = QtWidgets.QAction(Display.ACTION_EXIT, self.menubar)
        self.actionExit.setFont(self.getRegularFont())
        self.actionExit.setMenuRole(QtWidgets.QAction.QuitRole)
        self.actionExit.triggered.connect(self.close)

        self.actionAbout = QtWidgets.QAction(Display.ACTION_ABOUT, self.menubar)
        self.actionAbout.setFont(self.getRegularFont())
        self.actionAbout.setMenuRole(QtWidgets.QAction.AboutRole)
        self.actionAbout.triggered.connect(self.pop_up_action_about)
        
        self.actionConfig = QtWidgets.QAction(Display.ACTION_CONFIG, self.menubar)
        self.actionConfig.setFont(self.getRegularFont())
        self.actionConfig.setMenuRole(QtWidgets.QAction.NoRole)
        self.actionConfig.triggered.connect(self.pop_up_action_config)
        self.actionConfig.setEnabled(False)

        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionConfig)

    def setupStatusBar(self, LgClientDisplay):
        self.statusbar = QtWidgets.QStatusBar(LgClientDisplay)
        self.statusbar.setObjectName(Display.STATUS_BAR_OBJECT_NAME)
        LgClientDisplay.setStatusBar(self.statusbar)

    def setupSystemStatePanel(self):
        self.groupBox_system_state_panel = QtWidgets.QGroupBox()
        self.groupBox_system_state_panel.setFixedSize(Display.GROUPBOX_SYSTEM_STATE_WIDTH, Display.GROUPBOX_SYSTEM_STATE_HEIGHT)
        self.groupBox_system_state_panel.setSizePolicy(self.getFixedSizePolicy())
        self.groupBox_system_state_panel.setFont(self.getBoldFont(13))
        self.groupBox_system_state_panel.setStyleSheet(self.getPanelStyle())
        self.groupBox_system_state_panel.setObjectName(Display.GROUPBOX_SYSTEM_STATE_OBJECT_NAME)
        
        self.nonEditText_system_state = QtWidgets.QTextEdit(self.groupBox_system_state_panel)
        self.nonEditText_system_state.setGeometry(QtCore.QRect(Display.NON_EDIT_TEXT_LEFT, 
                                                               Display.NON_EDIT_TEXT_TOP, 
                                                               Display.NON_EDIT_TEXT_WIDHT, 
                                                               Display.NON_EDIT_TEXT_HEIGHT))
        self.nonEditText_system_state.setFont(self.getBoldFont(15))
        self.nonEditText_system_state.setStyleSheet(Style.NON_EDIT_TEXT_SYSTEM_STATE_STYLE)
        self.nonEditText_system_state.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nonEditText_system_state.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nonEditText_system_state.setReadOnly(True)
        self.nonEditText_system_state.setAlignment(QtCore.Qt.AlignCenter)
        self.nonEditText_system_state.setObjectName(Display.NON_EDIT_TEXT_OBJECT_NAME)

    def setupConnectionPanel(self):
        self.groupBox_connection_panel = QtWidgets.QGroupBox()
        self.groupBox_connection_panel.setFixedSize(Display.GROUPBOX_CONNECTION_WIDTH, Display.GROUPBOX_CONNECTION_HEIGHT)
        self.groupBox_connection_panel.setSizePolicy(self.getFixedSizePolicy())
        self.groupBox_connection_panel.setFont(self.getBoldFont(13))
        self.groupBox_connection_panel.setStyleSheet(self.getPanelStyle())
        self.groupBox_connection_panel.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.groupBox_connection_panel.setObjectName(Display.GROUPBOX_CONNECTION_OBJECT_NAME)
        
        self.pushButton_connection = QtWidgets.QPushButton(self.groupBox_connection_panel)
        self.pushButton_connection.setGeometry(QtCore.QRect(Display.BUTTON_CONNECTION_LEFT, 
                                                            Display.BUTTON_CONNECTION_TOP, 
                                                            Display.BUTTON_CONNECTION_WIDTH, 
                                                            Display.BUTTON_CONNECTION_HEIGHT))
        self.pushButton_connection.setFont(self.getRegularFont(11))
        self.pushButton_connection.setStyleSheet(self.getButtonStyle())
        self.pushButton_connection.setObjectName(Display.BUTTON_CONNECTION_OBJECT_NAME)
        self.applyShadowEffect(self.pushButton_connection)
        
        self.setupRemoteAddressGroup(self.groupBox_connection_panel)
        self.setupConnectionLayout(self.groupBox_connection_panel)

    def setupRemoteAddressGroup(self, parent):
        self.groupBox_remote_address = QtWidgets.QGroupBox(parent)
        self.groupBox_remote_address.setGeometry(QtCore.QRect(Display.GROUPBOX_REMOTE_ADDRESS_LEFT, 
                                                              Display.GROUPBOX_REMOTE_ADDRESS_TOP, 
                                                              Display.GROUPBOX_REMOTE_ADDRESS_WIDTH, 
                                                              Display.GROUPBOX_REMOTE_ADDRESS_HEIGHT))
        self.groupBox_remote_address.setSizePolicy(self.getFixedSizePolicy())
        self.groupBox_remote_address.setFont(self.getRegularFont(9))
        self.groupBox_remote_address.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_remote_address.setObjectName(Display.GROUPBOX_REMOTE_OBJECT_NAME)
        self.groupBox_remote_address.setStyleSheet(self.getGroupBoxStyle())
        
        self.editText_remote_address = QtWidgets.QLineEdit(self.groupBox_remote_address)
        self.editText_remote_address.setGeometry(QtCore.QRect(Display.EDIT_TEXT_REMOTE_ADDRESS_LEFT,
                                                              Display.EDIT_TEXT_REMOTE_ADDRESS_TOP,
                                                              Display.EDIT_TEXT_REMOTE_ADDRESS_WIDTH,
                                                              Display.EDIT_TEXT_REMOTE_ADDRESS_HEIGHT))
        self.editText_remote_address.setFont(self.getRegularFont(12))
        self.editText_remote_address.setStyleSheet(Style.EDIT_TEXT_BORDER_NON_STYLE)
        self.editText_remote_address.setObjectName(Display.EDIT_TEXT_REMOTE_ADDRESS_OBJECT_NAME)

    def setupConnectionLayout(self, parent):
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(Display.CON_HORIZONTAL_LAYOUT_LEFT, 
                                                             Display.CON_HORIZONTAL_LAYOUT_TOP, 
                                                             Display.CON_HORIZONTAL_LAYOUT_WIDTH, 
                                                             Display.CON_HORIZONTAL_LAYOUT_HEIGHT))
        self.horizontalLayoutWidget.setObjectName(Display.CON_HORIZONTAL_LAYOUT_OBJECT_NAME)
        
        self.connectionLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.connectionLayout.setObjectName(Display.CONNECTION_LAYOUT_OBJECT_NAME)
        
        self.gifLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.gifLabel.setSizePolicy(self.getFixedSizePolicy(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_HEIGHT))
        self.gifLabel.setMaximumSize(QtCore.QSize(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_HEIGHT))
        icon_pixmap = QtGui.QPixmap(self.resource_path(Display.GIF_ICON_PATH))
        scaled_pixmap = icon_pixmap.scaled(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_HEIGHT, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.gifLabel.setPixmap(scaled_pixmap)
        self.gifLabel.setObjectName(Display.GIF_LABEL_OBJECT_NAME)
        
        self.connectionLayout.addWidget(self.gifLabel)

    def setupModeControlPanel(self):
        self.groupBox_mode_control_panel = QtWidgets.QGroupBox()
        self.groupBox_mode_control_panel.setFixedSize(Display.GROUPBOX_CONTROL_PANEL_WIDTH, Display.GROUPBOX_CONTROL_PANEL_HEIGHT)
        self.groupBox_mode_control_panel.setFont(self.getBoldFont(13))
        self.groupBox_mode_control_panel.setStyleSheet(self.getPanelStyle())
        self.groupBox_mode_control_panel.setObjectName(Display.GROUPBOX_MODE_CONTROL_PANEL_OBJECT_NAME)
        self.groupBox_mode_control_panel.setEnabled(False)
        self.groupBox_mode_control_panel.setStyleSheet(self.getDisabledPanelStyle())
        
        self.setupPreArmCodeGroup(self.groupBox_mode_control_panel)
        self.setupArmModeGroup(self.groupBox_mode_control_panel)
        
        self.pushButton_pre_arm_mode = QtWidgets.QPushButton(self.groupBox_mode_control_panel)
        self.pushButton_pre_arm_mode.setGeometry(QtCore.QRect(Display.BUTTON_PRE_ARM_MODE_LEFT, 
                                                              Display.BUTTON_PRE_ARM_MODE_TOP, 
                                                              Display.BUTTON_PRE_ARM_MODE_WIDTH, 
                                                              Display.BUTTON_PRE_ARM_MODE_HEIGHT))
        self.pushButton_pre_arm_mode.setFont(self.getRegularFont(11))
        self.pushButton_pre_arm_mode.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_pre_arm_mode.setCheckable(True)
        self.pushButton_pre_arm_mode.setObjectName(Display.BUTTON_PRE_ARM_MODE_OBJECT_NAME)
        self.applyShadowEffect(self.pushButton_pre_arm_mode)
        
        self.pushButton_safe_mode = QtWidgets.QPushButton(self.groupBox_mode_control_panel)
        self.pushButton_safe_mode.setGeometry(QtCore.QRect(Display.BUTTON_SAFE_MODE_LEFT, 
                                                           Display.BUTTON_SAFE_MODE_TOP, 
                                                           Display.BUTTON_SAFE_MODE_WIDTH, 
                                                           Display.BUTTON_SAFE_MODE_HEIGHT))
        self.pushButton_safe_mode.setFont(self.getRegularFont(11))
        self.pushButton_safe_mode.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_safe_mode.setCheckable(True)
        self.pushButton_safe_mode.setObjectName(Display.BUTTON_SAFE_MODE_OBJECT_NAME)
        self.applyShadowEffect(self.pushButton_safe_mode)

    def setupPreArmCodeGroup(self, parent):
        self.groupBox_pre_arm_code = QtWidgets.QGroupBox(parent)
        self.groupBox_pre_arm_code.setGeometry(QtCore.QRect(Display.GROUPBOX_PRE_ARM_CODE_LEFT, 
                                                            Display.GROUPBOX_PRE_ARM_CODE_TOP, 
                                                            Display.GROUPBOX_PRE_ARM_CODE_WIDTH, 
                                                            Display.GROUPBOX_PRE_ARM_CODE_HEIGHT))
        self.groupBox_pre_arm_code.setSizePolicy(self.getFixedSizePolicy())
        self.groupBox_pre_arm_code.setFont(self.getRegularFont(9))
        self.groupBox_pre_arm_code.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_pre_arm_code.setObjectName(Display.GROUPBOX_PRE_ARM_CODE_OBJECT_NAME)
        self.groupBox_pre_arm_code.setStyleSheet(self.getGroupBoxStyle())
        self.groupBox_pre_arm_code.setEnabled(False)
        
        self.editText_pre_arm_code = QtWidgets.QLineEdit(self.groupBox_pre_arm_code)
        self.editText_pre_arm_code.setGeometry(QtCore.QRect(Display.EDIT_TEXT_PRE_ARM_LEFT, 
                                                            Display.EDIT_TEXT_PRE_ARM_TOP,
                                                            Display.EDIT_TEXT_PRE_ARM_WIDTH, 
                                                            Display.EDIT_TEXT_PRE_ARM_HEIGHT))
        self.editText_pre_arm_code.setFont(self.getRegularFont(12))
        self.editText_pre_arm_code.setStyleSheet(Style.EDIT_TEXT_BORDER_NON_STYLE)
        self.editText_pre_arm_code.setReadOnly(False)
        self.editText_pre_arm_code.setText("")
        self.editText_pre_arm_code.setEchoMode(QtWidgets.QLineEdit.Password)
        self.editText_pre_arm_code.setObjectName(Display.EDIT_TEXT_PRE_ARM_OBJECT_NAME)

    def setupArmModeGroup(self, parent):
        self.groupBox_arm_mode = QtWidgets.QGroupBox(parent)
        self.groupBox_arm_mode.setEnabled(False)
        self.groupBox_arm_mode.setGeometry(QtCore.QRect(Display.GROUPBOX_ARM_MODE_LEFT, 
                                                        Display.GROUPBOX_ARM_MODE_TOP, 
                                                        Display.GROUPBOX_ARM_MODE_WIDTH, 
                                                        Display.GROUPBOX_ARM_MODE_HEIGHT))
        self.groupBox_arm_mode.setSizePolicy(self.getFixedSizePolicy())
        self.groupBox_arm_mode.setFont(self.getRegularFont(9))
        self.groupBox_arm_mode.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_arm_mode.setObjectName(Display.GROUPBOX_ARM_MODE_OBJECT_NAME)
        self.groupBox_arm_mode.setStyleSheet(self.getGroupBoxStyle())
        
        self.pushButton_armed_manual = QtWidgets.QPushButton(self.groupBox_arm_mode)
        self.pushButton_armed_manual.setGeometry(QtCore.QRect(Display.BUTTON_ARMED_MANUAL_LEFT, 
                                                              Display.BUTTON_ARMED_MANUAL_TOP, 
                                                              Display.BUTTON_ARMED_MANUAL_WIDTH, 
                                                              Display.BUTTON_ARMED_MANUAL_HEIGHT))
        self.pushButton_armed_manual.setFont(self.getRegularFont(11))
        self.pushButton_armed_manual.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_armed_manual.setCheckable(True)
        self.pushButton_armed_manual.setObjectName(Display.BUTTON_ARMED_MANUAL_OBJECT_NAME)
        self.applyShadowEffect(self.pushButton_armed_manual)
        
        self.pushButton_auto_engage = QtWidgets.QPushButton(self.groupBox_arm_mode)
        self.pushButton_auto_engage.setGeometry(QtCore.QRect(Display.BUTTON_AUTO_ENGAGE_LEFT, 
                                                             Display.BUTTON_AUTO_ENGAGE_TOP, 
                                                             Display.BUTTON_AUTO_ENGAGE_WIDTH, 
                                                             Display.BUTTON_AUTO_ENGAGE_HEIGHT))
        self.pushButton_auto_engage.setFont(self.getRegularFont(11))
        self.pushButton_auto_engage.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_auto_engage.setCheckable(True)
        self.pushButton_auto_engage.setObjectName(Display.BUTTON_AUTO_ENGAGE_OBJECT_NAME)
        self.pushButton_auto_engage.clicked.connect(self.enter_auto_engage_mode)
        self.applyShadowEffect(self.pushButton_auto_engage)

    def setupCommandPanel(self):
        self.groupBox_command_panel = QtWidgets.QGroupBox()
        self.groupBox_command_panel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.groupBox_command_panel.setMaximumHeight(0)
        self.groupBox_command_panel.setFont(self.getBoldFont(13))
        self.groupBox_command_panel.setObjectName(Display.GROUPBOX_COMMAND_PANEL_OBJECT_NAME)
        self.groupBox_command_panel.setStyleSheet(self.getPanelStyle())

        self.stackedWidget = QtWidgets.QStackedWidget(self.groupBox_command_panel)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, Display.GROUPBOX_COMMAND_PANEL_WIDTH, Display.GROUPBOX_COMMAND_PANEL_HEIGHT))
        self.stackedWidget.setContentsMargins(0, 10, 0, 0)

        self.setupCommandPanelManual()
        self.setupCommandPanelAuto()

        self.stackedWidget.addWidget(self.auto_widget)
        self.stackedWidget.addWidget(self.manual_widget)
        
        self.stackedWidget.setCurrentIndex(Display.COMMAND_WIDGET_MANUAL)

    def setupCommandPanelManual(self):
        self.manual_widget = QtWidgets.QWidget()
        self.manual_layout = QtWidgets.QVBoxLayout(self.manual_widget)
        self.manual_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.checkbox_laser = QtWidgets.QCheckBox(Display.CHECKBOX_LASER)
        self.checkbox_laser.setContentsMargins(0, 0, 5, 0)
        self.checkbox_cal = QtWidgets.QCheckBox(Display.CHECKBOX_CAL)
        self.checkbox_layout.addWidget(self.checkbox_laser)
        self.checkbox_layout.addWidget(self.checkbox_cal)
        self.checkbox_layout.setContentsMargins(0, 0, 0, 10)

        icon_size = QtCore.QSize(Display.MANUAL_DIRECTION_KEY_ICON_SIZE, Display.MANUAL_DIRECTION_KEY_ICON_SIZE)
        self.button_up = QtWidgets.QPushButton()
        self.button_up.setIcon(QtGui.QIcon(self.resource_path(Display.UP_KEY_ICON_PATH)))
        self.button_up.setIconSize(icon_size)
        self.button_up.setFixedSize(icon_size)
        self.button_up.setStyleSheet(self.getButtonManualStyle())
        self.button_up.setContentsMargins(0, 0, 0, 5)
        self.button_up.setObjectName(Display.KEY_UP_1)
        
        self.button_up_layout = QtWidgets.QHBoxLayout()
        self.button_up_layout.addWidget(self.button_up)
        self.button_up_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.button_up_layout.setContentsMargins(0, 0, 0, 4)
        
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.button_layout.setSpacing(15)
        
        self.button_left = QtWidgets.QPushButton()
        self.button_left.setIcon(QtGui.QIcon(self.resource_path(Display.LEFT_KEY_ICON_PATH)))
        self.button_left.setIconSize(icon_size)
        self.button_left.setFixedSize(icon_size)
        self.button_left.setStyleSheet(self.getButtonManualStyle())
        self.button_left.setObjectName(Display.KEY_LEFT_1)
        
        self.button_down = QtWidgets.QPushButton()
        self.button_down.setIcon(QtGui.QIcon(self.resource_path(Display.DOWN_KEY_ICON_PATH)))
        self.button_down.setIconSize(icon_size)
        self.button_down.setFixedSize(icon_size)
        self.button_down.setStyleSheet(self.getButtonManualStyle())
        self.button_down.setObjectName(Display.KEY_DOWN_1)
        
        self.button_right = QtWidgets.QPushButton()
        self.button_right.setIcon(QtGui.QIcon(self.resource_path(Display.RIGHT_KEY_ICON_PATH)))
        self.button_right.setIconSize(icon_size)
        self.button_right.setFixedSize(icon_size)
        self.button_right.setStyleSheet(self.getButtonManualStyle())
        self.button_right.setObjectName(Display.KEY_RIGHT_1)
        
        self.button_layout.addWidget(self.button_left)
        self.button_layout.addWidget(self.button_down)
        self.button_layout.addWidget(self.button_right)
        
        self.button_fire = QtWidgets.QPushButton()
        self.button_fire.setIcon(QtGui.QIcon(self.resource_path(Display.FIRE_KEY_ICON_PATH)))
        self.button_fire.setIconSize(QtCore.QSize(Display.MANUAL_FIRE_KEY_ICON_WIDTH, Display.MANUAL_FIRE_KEY_ICON_HEIGHT))
        self.button_fire.setFixedSize(QtCore.QSize(Display.MANUAL_FIRE_KEY_ICON_WIDTH, Display.MANUAL_FIRE_KEY_ICON_HEIGHT))
        self.button_fire.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_fire.setStyleSheet(self.getButtonManualStyle())
        self.button_fire.setObjectName(Display.KEY_FIRE_1)
        
        self.fire_button_layout = QtWidgets.QHBoxLayout()
        self.fire_button_layout.addWidget(self.button_fire)
        self.fire_button_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.manual_layout.addLayout(self.checkbox_layout)
        self.manual_layout.addLayout(self.button_up_layout)
        self.manual_layout.addLayout(self.button_layout)
        self.manual_layout.addLayout(self.fire_button_layout)

    def setupCommandPanelAuto(self):
        self.auto_widget = QtWidgets.QWidget()
        self.auto_layout = QtWidgets.QVBoxLayout(self.auto_widget)
        self.auto_layout.setContentsMargins(20, 7, 0, 0)

        self.widget_key = QtWidgets.QWidget(self.auto_widget)
        self.widget_key.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setupTargetOrderGroup(self.auto_widget)
        self.setupSequenceButtons(self.widget_key)
        self.auto_layout.addWidget(self.groupBox_target_order)
        self.auto_layout.addWidget(self.widget_key)

    def setupTargetOrderGroup(self, parent):
        self.groupBox_target_order = QtWidgets.QGroupBox(parent)
        self.groupBox_target_order.setMaximumWidth(Display.GROUPBOX_TARGET_ORDER_WIDTH)
        self.groupBox_target_order.setMaximumHeight(Display.GROUPBOX_TARGET_ORDER_HEIGHT)
        self.groupBox_target_order.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.groupBox_target_order.setFont(self.getRegularFont(9))
        self.groupBox_target_order.setObjectName(Display.GROUPBOX_TARGET_ORDER_OBJECT_NAME)
        self.groupBox_target_order.setStyleSheet(self.getGroupBoxStyle())
        
        layout = QtWidgets.QVBoxLayout(self.groupBox_target_order)
        layout.addStretch(1)
        
        self.editText_target_order = NumericPlainTextEdit(self.groupBox_target_order)
        self.editText_target_order.setGeometry(0, 0, Display.GROUPBOX_TARGET_ORDER_WIDTH-10, Display.GROUPBOX_TARGET_ORDER_HEIGHT-10)
        self.editText_target_order.setFont(self.getRegularFont(12))
        self.editText_target_order.setStyleSheet(Style.EDIT_TEXT_BORDER_NON_STYLE)
        self.editText_target_order.setReadOnly(False)
        self.editText_target_order.setText("")
        self.editText_target_order.setObjectName(Display.EDIT_TEXT_TARGET_ORDER_OBJECT_NAME)
        
        layout.addWidget(self.editText_target_order)
        layout.addStretch(1)
    
        self.groupBox_target_order.setLayout(layout)

    def setupSequenceButtons(self, parent):
        button_names = [Display.BUTTON_KEY_1_OBJECT_NAME, Display.BUTTON_KEY_2_OBJECT_NAME, Display.BUTTON_KEY_3_OBJECT_NAME,
                        Display.BUTTON_KEY_4_OBJECT_NAME, Display.BUTTON_KEY_5_OBJECT_NAME, Display.BUTTON_KEY_6_OBJECT_NAME,
                        Display.BUTTON_KEY_7_OBJECT_NAME, Display.BUTTON_KEY_8_OBJECT_NAME, Display.BUTTON_KEY_9_OBJECT_NAME,
                        Display.BUTTON_KEY_STOP_OBJECT_NAME, Display.BUTTON_KEY_0_OBJECT_NAME, Display.BUTTON_KEY_PLAY_PAUSE_OBJECT_NAME]
        button_positions = [(10, 5), (95, 5), (180, 5),
                            (10, 54), (95, 54), (180, 54),
                            (10, 104), (95, 104), (180, 104),
                            (10, 154), (95, 154), (180, 154)]

        for name, pos in zip(button_names, button_positions):
            button = QtWidgets.QPushButton(parent)
            button.setGeometry(QtCore.QRect(pos[0], pos[1], Display.BUTTON_KEY_WIDTH, Display.BUTTON_KEY_HEIGHT))
            button.setFont(self.getRegularFont(12))
            button.setStyleSheet(self.getButtonStyle())
            button.setObjectName(name)
            button.clicked.connect(self.target_button_clicked)
            if name == Display.BUTTON_KEY_PLAY_PAUSE_OBJECT_NAME:
                self.pushButton_auto_start = button
            elif name == Display.BUTTON_KEY_STOP_OBJECT_NAME:
                self.pushButton_auto_stop = button
            self.applyShadowEffect(button)
            setattr(self, name, button)

        self.play_pause_icon = QtGui.QIcon()
        self.play_pause_icon.addPixmap(QtGui.QPixmap(self.resource_path(Display.PLAY_PAUSE_ICON_PATH)))
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(Display.PAUSE_ICON_PATH))
        self.pushButton_auto_start.setIcon(self.play_pause_icon)
        self.pushButton_auto_start.setCheckable(True)
        self.pushButton_auto_start.setIconSize(QtCore.QSize(Display.PLAY_PAUSE_STOP_ICON_SIZE, Display.PLAY_PAUSE_STOP_ICON_SIZE))
        self.pushButton_auto_start.disconnect()
        self.pushButton_auto_start.clicked.connect(self.auto_engage_toggle)

        stop_icon = QtGui.QIcon()
        stop_icon.addPixmap(QtGui.QPixmap(self.resource_path(Display.STOP_ICON_PATH)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_auto_stop.setIcon(stop_icon)
        self.pushButton_auto_stop.setIconSize(QtCore.QSize(Display.PLAY_PAUSE_STOP_ICON_SIZE, Display.PLAY_PAUSE_STOP_ICON_SIZE))
        self.pushButton_auto_stop.disconnect()

    def setupLogPanel(self):
        self.nonEditText_log = QtWidgets.QTextEdit()
        self.nonEditText_log.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.nonEditText_log.setFont(self.getRegularFont(11))
        self.nonEditText_log.setStyleSheet(Style.NONEDIT_TEXT_LOG_STYLE)
        self.nonEditText_log.setLineWidth(1)
        self.nonEditText_log.setReadOnly(True)
        self.nonEditText_log.setObjectName(Display.NONEDIT_TEXT_LOG_OBJECT_NAME)

    def setupAlgoSelectionPanel(self):
        self.groupBox_algo = QtWidgets.QGroupBox()
        self.groupBox_algo.setEnabled(False)
        self.groupBox_algo.setMaximumWidth(Display.GROUPBOX_ALGORITHM_WIDTH)
        self.groupBox_algo.setMaximumHeight(Display.GROUPBOX_ALGORITHM_HEIGHT)
        self.groupBox_algo.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.groupBox_algo.setFont(self.getBoldFont(13))
        self.groupBox_algo.setObjectName(Display.GROUPBOX_ALGORITHM_OBJECT_NAME)
        self.groupBox_algo.setStyleSheet(self.getDisabledPanelStyle())
        
        self.algoHorizontalLayoutWidget = QtWidgets.QWidget(self.groupBox_algo)
        self.algoHorizontalLayout = QtWidgets.QHBoxLayout(self.algoHorizontalLayoutWidget)
        self.algoHorizontalLayout.setContentsMargins(10, 10, 10, 10)
        
        self.pushButton_algo_cv = QtWidgets.QPushButton(self.algoHorizontalLayoutWidget)
        self.pushButton_algo_cv.setMinimumWidth(Display.BUTTON_ALGO_WIDTH)
        self.pushButton_algo_cv.setGeometry(QtCore.QRect(0, 0, 
                                                        Display.BUTTON_ALGO_WIDTH, 
                                                        Display.BUTTON_ALGO_HEIGHT))
        self.pushButton_algo_cv.setFont(self.getRegularFont(10))
        self.pushButton_algo_cv.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_algo_cv.setCheckable(True)
        icon = QtGui.QIcon(Display.BUTTON_OPEN_CV_ICON_PATH)
        self.pushButton_algo_cv.setIcon(icon)
        self.pushButton_algo_cv.setIconSize(QtCore.QSize(Display.BUTTON_ALGO_ICON_WIDTH,
                                                         Display.BUTTON_ALGO_ICON_HEIGHT))
        self.pushButton_algo_cv.clicked.connect(self.algo_button_clicked)
        self.applyShadowEffect(self.pushButton_algo_cv)

        self.pushButton_algo_tf = QtWidgets.QPushButton(self.algoHorizontalLayoutWidget)
        self.pushButton_algo_tf.setMinimumWidth(Display.BUTTON_ALGO_WIDTH)
        self.pushButton_algo_tf.setGeometry(QtCore.QRect(0, 0, 
                                                        Display.BUTTON_ALGO_WIDTH, 
                                                        Display.BUTTON_ALGO_HEIGHT))
        self.pushButton_algo_tf.setFont(self.getRegularFont(10))
        self.pushButton_algo_tf.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_algo_tf.setCheckable(True)
        icon = QtGui.QIcon(Display.BUTTON_TENSOR_FLOW_ICON_PATH)
        self.pushButton_algo_tf.setIcon(icon)
        self.pushButton_algo_tf.setIconSize(QtCore.QSize(Display.BUTTON_ALGO_ICON_WIDTH,
                                                         Display.BUTTON_ALGO_ICON_HEIGHT))
        self.pushButton_algo_tf.clicked.connect(self.algo_button_clicked)
        self.applyShadowEffect(self.pushButton_algo_tf)
        
        self.algoHorizontalLayout.addWidget(self.pushButton_algo_cv)
        self.algoHorizontalLayout.addWidget(self.pushButton_algo_tf)
        self.groupBox_algo.setLayout(self.algoHorizontalLayout)

    def setupRobotActionPanel(self):
        self.groupBox_robot_action = QtWidgets.QGroupBox()
        self.groupBox_robot_action.setEnabled(True)
        self.groupBox_robot_action.setMaximumHeight(Display.GROUPBOX_ALGORITHM_HEIGHT)
        self.groupBox_robot_action.setMinimumWidth(Display.GROUPBOX_ROBOT_ACTION_WIDTH)
        self.groupBox_robot_action.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.groupBox_robot_action.setFont(self.getBoldFont(13))
        self.groupBox_robot_action.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_robot_action.setStyleSheet(self.getPanelStyle())
        self.groupBox_robot_action.hide()

        self.robotActionHorizontalLayoutWidget = QtWidgets.QWidget(self.groupBox_robot_action)
        self.robotActionHorizontalLayout = QtWidgets.QHBoxLayout(self.robotActionHorizontalLayoutWidget)
        self.robotActionHorizontalLayout.setContentsMargins(10, 10, 10, 10)
        
        self.nonEdit_robot_action = QtWidgets.QLineEdit(self.robotActionHorizontalLayoutWidget)
        self.nonEdit_robot_action.setFont(self.getBoldFont(15))
        self.nonEdit_robot_action.setStyleSheet(Style.NON_EDIT_TEXT_SYSTEM_STATE_STYLE)
        self.nonEdit_robot_action.setReadOnly(True)
        
        self.robotActionHorizontalLayout.addWidget(self.nonEdit_robot_action)
        self.groupBox_robot_action.setLayout(self.robotActionHorizontalLayout)
    
    def setupRecordPlayPanel(self):
        self.groupBox_record_play = QtWidgets.QGroupBox()
        self.groupBox_record_play.setEnabled(True)
        self.groupBox_record_play.setMaximumHeight(Display.GROUPBOX_ALGORITHM_HEIGHT)
        self.groupBox_record_play.setMaximumWidth(Display.GROUPBOX_ALGORITHM_WIDTH)
        self.groupBox_record_play.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.groupBox_record_play.setFont(self.getBoldFont(13))
        self.groupBox_record_play.setStyleSheet(self.getPanelStyle())
        self.groupBox_record_play.setAlignment(QtCore.Qt.AlignCenter)

        self.recordPlayHorizontalLayoutWidget = QtWidgets.QWidget(self.groupBox_record_play)
        self.recordPlayHorizontalLayout = QtWidgets.QHBoxLayout(self.recordPlayHorizontalLayoutWidget)
        
        self.pushButton_record = QtWidgets.QPushButton(self.recordPlayHorizontalLayoutWidget)
        self.pushButton_record.setFixedSize(Display.BUTTON_RECORD_ICON_WIDTH, Display.BUTTON_RECORD_ICON_HEIGHT)
        self.gifRecordLabel = QtWidgets.QLabel(self.pushButton_record)
        self.gifRecordLabel.setGeometry(self.pushButton_record.rect())
        self.gifRecordLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        self.recordMovie = QMovie(self.resource_path(Display.BUTTON_RECORD_ICON_PATH))
        self.recordMovie.setScaledSize(QtCore.QSize(Display.BUTTON_RECORD_ICON_WIDTH, Display.BUTTON_RECORD_ICON_HEIGHT))
        self.recordMovie.setSpeed(Display.GIF_SPEED)
        
        self.recordMovieDisabled = QMovie(self.resource_path(Display.BUTTON_RECORD_DISABLED_ICON_PATH))
        self.recordMovieDisabled.setScaledSize(QtCore.QSize(Display.BUTTON_RECORD_ICON_WIDTH, Display.BUTTON_RECORD_ICON_HEIGHT))
        self.recordMovieDisabled.setSpeed(Display.GIF_SPEED)
        
        self.gifRecordLabel.setMovie(self.recordMovieDisabled)
        self.pushButton_record.clicked.connect(self.on_record_clicked)
        
        self.pushButton_play = QtWidgets.QPushButton(self.recordPlayHorizontalLayoutWidget)
        self.pushButton_play.setFixedSize(Display.BUTTON_RECORD_ICON_WIDTH, Display.BUTTON_RECORD_ICON_HEIGHT)
        gifPlayLabel = QtWidgets.QLabel(self.pushButton_play)
        gifPlayLabel.setGeometry(self.pushButton_play.rect())
        gifPlayLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.playMovie = QMovie(self.resource_path(Display.BUTTON_PLAY_ICON_PATH))
        self.playMovie.setScaledSize(QtCore.QSize(Display.BUTTON_RECORD_ICON_WIDTH, Display.BUTTON_RECORD_ICON_HEIGHT))
        self.playMovie.setSpeed(Display.GIF_SPEED)
        gifPlayLabel.setMovie(self.playMovie)
        self.pushButton_play.clicked.connect(self.on_play_clicked)
        self.playMovie.start()
        self.playMovie.stop()
        self.playMovie.jumpToFrame(0)

        self.recordPlayHorizontalLayout.addWidget(self.pushButton_record)
        self.recordPlayHorizontalLayout.addWidget(self.pushButton_play)
        self.groupBox_record_play.setLayout(self.recordPlayHorizontalLayout)
    
    def setupCameraVideoPanel(self):
        self.groupBox_camera_video = QtWidgets.QGroupBox()
        self.groupBox_camera_video.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.groupBox_camera_video.setFont(self.getBoldFont(13))
        self.groupBox_camera_video.setStyleSheet(self.getPanelStyle())
        self.groupBox_camera_video.setObjectName(Display.GROUPBOX_CAMERA_VIDEO_OBJECT_NAME)
        
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox_camera_video)
        self.verticalLayoutWidget.setObjectName(Display.CAMERA_VERTICAL_LAYOUT_WIDGET_OBJECT_NAME)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName(Display.CAMERA_VERTICAL_LAYOUTE_OBJECT_NAME)
        
        self.label_camera_video = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_camera_video.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label_camera_video.setStyleSheet(Style.LABEL_CAMERA_STYLE)
        self.label_camera_video.setAlignment(QtCore.Qt.AlignCenter)
        self.label_camera_video.setObjectName(Display.LABEL_CAMERA_VIDEO_OBJECT_NAME)
        
        self.overlayWidget = QtWidgets.QWidget(self.label_camera_video)
        self.overlayWidget.setGeometry(self.label_camera_video.width(), 
                                       0, 
                                       50 + Display.OVERLAY_RECORD_ICON_PADDING,
                                       50)
        self.overlayWidget.setStyleSheet(Style.OVERLAY_STYLE)
        
        self.iconLabel = QtWidgets.QLabel(self.overlayWidget)
        self.iconLabel.setPixmap(QtGui.QPixmap(Display.OVERLAY_RECORD_ICON))
        self.iconLabel.setScaledContents(True)
        self.iconLabel.setGeometry(0, 0, 50, 50)
        self.iconLabel.hide()
        
        self.verticalLayout.addWidget(self.label_camera_video)
        self.groupBox_camera_video.setLayout(self.verticalLayout)

        self.label_camera_video.resizeEvent = self.onLabelCameraVideoResize

    def onLabelCameraVideoResize(self, event):
        self.overlayWidget.move(self.label_camera_video.width() - self.overlayWidget.width(), 0)
        event.accept()

    def retranslateUi(self, LgClientDisplay):
        _translate = QtCore.QCoreApplication.translate
        LgClientDisplay.setWindowTitle(_translate(Display.WINDOW_TITLE, Display.WINDOW_TITLE))
        self.groupBox_connection_panel.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_CONNECTION_TITLE))
        self.pushButton_connection.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_CONNECTION_TITLE_CONNECT))
        self.groupBox_remote_address.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_REMOTE_ADDRESS_TITLE))
        self.editText_remote_address.setText(_translate(Display.WINDOW_TITLE, Display.EDIT_TEXT_REMOTE_ADDRESS_DEFAULT_TEXT))
        self.groupBox_algo.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_ALGORITHM_TITLE))
        self.groupBox_robot_action.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_ROBOT_ACTION_TITLE))
        self.groupBox_record_play.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_RECORD_PLAY_TITLE))
        self.pushButton_algo_cv.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_OPEN_CV_TITLE))
        self.pushButton_algo_tf.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_TENSOR_FLOW_TITLE))
        self.groupBox_camera_video.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_CAMERA_VIDEO_TITLE))
        self.groupBox_system_state_panel.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_SYSTEM_STATE_TITLE))
        self.nonEditText_system_state.setPlainText(_translate(Display.WINDOW_TITLE, Display.NON_EDIT_TEXT_DEFAULT_TEXT))
        self.nonEditText_system_state.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_mode_control_panel.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_CONTROL_PANEL_TITLE))
        self.groupBox_arm_mode.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_ARM_MODE_TITLE))
        self.pushButton_armed_manual.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_ARMED_MANUAL_TITLE))
        self.pushButton_auto_engage.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_AUTO_ENGAGE_TITLE))
        self.groupBox_pre_arm_code.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_PRE_ARM_CODE_TITLE))
        self.pushButton_pre_arm_mode.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_PRE_ARM_MODE_TITLE))
        self.pushButton_safe_mode.setText(_translate(Display.WINDOW_TITLE, Display.BUTTON_SAFE_MODE_TITLE))
        self.groupBox_command_panel.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_COMMAND_PANEL_TITLE))
        self.pushButton_key_1.setText(_translate(Display.WINDOW_TITLE, "1"))
        self.pushButton_key_2.setText(_translate(Display.WINDOW_TITLE, "2"))
        self.pushButton_key_3.setText(_translate(Display.WINDOW_TITLE, "3"))
        self.pushButton_key_4.setText(_translate(Display.WINDOW_TITLE, "4"))
        self.pushButton_key_5.setText(_translate(Display.WINDOW_TITLE, "5"))
        self.pushButton_key_6.setText(_translate(Display.WINDOW_TITLE, "6"))
        self.pushButton_key_7.setText(_translate(Display.WINDOW_TITLE, "7"))
        self.pushButton_key_8.setText(_translate(Display.WINDOW_TITLE, "8"))
        self.pushButton_key_9.setText(_translate(Display.WINDOW_TITLE, "9"))
        self.pushButton_key_0.setText(_translate(Display.WINDOW_TITLE, "0"))
        self.groupBox_target_order.setTitle(_translate(Display.WINDOW_TITLE, Display.GROUPBOX_TARGET_ORDER_TITLE))
        self.menuFile.setTitle(_translate(Display.WINDOW_TITLE, Display.MENUFILE_TEXT))
        self.menuHelp.setTitle(_translate(Display.WINDOW_TITLE, Display.MENUHELP_TEXT))
        self.actionExit.setText(_translate(Display.WINDOW_TITLE, Display.MENUEXIT_TEXT))
        self.actionAbout.setText(_translate(Display.WINDOW_TITLE, Display.MENUABOUT_TEXT))
        self.actionConfig.setText(_translate(Display.WINDOW_TITLE, Display.MENUACONFIG_TEXT))

    def getRegularFont(self, pointSize=11):
        font = QtGui.QFont()
        font.setFamily(Display.FONT_FAMILY)
        font.setPointSize(pointSize)
        return font

    def getBoldFont(self, pointSize=11):
        font = self.getRegularFont(pointSize)
        font.setBold(True)
        font.setWeight(75)
        return font

    def getFixedSizePolicy(self, horizontalStretch=0, verticalStretch=0):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(horizontalStretch)
        sizePolicy.setVerticalStretch(verticalStretch)
        return sizePolicy

    def getGroupBoxStyle(self):
        return Style.GROUPBOX_STYLE

    def getDisabledGroupBoxStyle(self):
        return Style.GROUPBOX_DISABLED_STYLE
    
    def getPanelStyle(self):
        return Style.PANEL_GROUPBOX_STYLE
    
    def getDisabledPanelStyle(self):
        return Style.PANEL_GROUPBOX_DISABLED_STYLE

    def getButtonStyle(self):
        return Style.BUTTON_STYLE
    
    def getSelectedButtonStyle(self):
        return Style.BUTTON_SELECTED_STYLE
    
    def getDisabledButtonStyle(self):
        return Style.BUTTON_DISABLED_STYLE
    
    def getButtonManualStyle(self):
        return Style.BUTTON_MANUAL_STYLE
    
    def getMenuBarStyle(self):
        return Style.MENU_BAR_STYLE

    def getMenuStyle(self):
        return Style.MENU_STYLE
    
    def slide_down(self, groupbox, height):
        if groupbox.maximumHeight() == height:
            return
        self.animation = QtCore.QPropertyAnimation(groupbox, b"maximumHeight")
        self.animation.setDuration(100)
        self.animation.setStartValue(0)
        self.animation.setEndValue(height)
        self.animation.finished.connect(lambda: self.adjust_groupbox_height(groupbox, height))
        self.animation.start()

    def slide_up(self, groupbox, height):
        if groupbox.maximumHeight() == 0:
            return
        self.animation = QtCore.QPropertyAnimation(groupbox, b"maximumHeight")
        self.animation.setDuration(100)
        self.animation.setStartValue(height)
        self.animation.setEndValue(0)
        self.animation.finished.connect(lambda: self.adjust_groupbox_height(groupbox, 0))
        self.animation.start()

    def adjust_groupbox_height(self, groupbox, height):
        groupbox.setMaximumHeight(height)
        groupbox.setMinimumHeight(height)
        groupbox.updateGeometry()

    def applyShadowEffect(self, button):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        button.setGraphicsEffect(shadow)

    def update_log(self, log_messages):
        self.nonEditText_log.setHtml("\n".join(log_messages))
        self.scroll_log_to_last_line()
        
    def scroll_log_to_last_line(self):
        cursor = self.nonEditText_log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.nonEditText_log.setTextCursor(cursor)
        self.nonEditText_log.ensureCursorVisible()

    def target_button_clicked(self):
        sender = self.sender()
        clickedNumber = sender.text()
        currentTargetOrder = self.editText_target_order.text()
        self.editText_target_order.setText(currentTargetOrder + clickedNumber)
    
    def connection_state_changed(self, connected):
        self.networkConnected = connected
        if connected == Network.NETWORK_CONNECTED:
            self.pushButton_connection.setText(Display.BUTTON_CONNECTION_TITLE_DISCONNECT)
            movie = QMovie(self.resource_path(Display.GIF_ICON_CONNECTED_PATH))
            movie.setSpeed(Display.GIF_SPEED)
            movie.setScaledSize(QtCore.QSize(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_WIDTH))
            movie.start()
            self.gifLabel.setMovie(movie)
            self.pushButton_connection.setStyleSheet(self.getSelectedButtonStyle())
        elif connected == Network.NETWORK_DISCONNECTED:
            self.pushButton_connection.setText(Display.BUTTON_CONNECTION_TITLE_CONNECT)
            icon_pixmap = QtGui.QPixmap(self.resource_path(Display.GIF_ICON_PATH))
            scaled_pixmap = icon_pixmap.scaled(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_WIDTH, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.gifLabel.setPixmap(scaled_pixmap)
            self.pushButton_connection.setStyleSheet(self.getButtonStyle())
        else:
            self.pushButton_connection.setText(Display.BUTTON_CONNECTION_TITLE_DISCONNECT)
            movie = QMovie(self.resource_path(Display.GIF_ICON_PATH))
            movie.setSpeed(Display.GIF_SPEED)
            movie.setScaledSize(QtCore.QSize(Display.GIF_LABEL_WIDTH, Display.GIF_LABEL_WIDTH))
            movie.start()
            self.gifLabel.setMovie(movie)
            
    def system_state_changed(self, state):
        if self.networkConnected == Network.NETWORK_DISCONNECTED:
            self.enter_unknown_mode()
            return
        mode = self.extract_system_mode(state)
        self.nonEditText_system_state.setText(Setting.SYSTEM_MODE_DICT[mode])
        self.nonEditText_system_state.setAlignment(QtCore.Qt.AlignCenter)
        if mode in self.stateFuncDict:
            self.stateFuncDict[mode]()
    
    def extract_system_mode(self, state):
        for mode in Setting.SYSTEM_MODE_LIST:
            if state & mode:
                return mode
        return Setting.SYSTEM_MODE_UNKNOWN
    
    def enter_unknown_mode(self):
        self.editText_target_order.clear()
        self.slide_up(self.groupBox_command_panel, Display.GROUPBOX_COMMAND_PANEL_HEIGHT)
        self.groupBox_mode_control_panel.setStyleSheet(self.getDisabledPanelStyle())
        self.groupBox_mode_control_panel.setEnabled(False)
        self.groupBox_pre_arm_code.setStyleSheet(self.getDisabledGroupBoxStyle())
        self.groupBox_pre_arm_code.setEnabled(False)
        self.groupBox_arm_mode.setStyleSheet(self.getDisabledGroupBoxStyle())
        self.groupBox_arm_mode.setEnabled(False)
        self.pushButton_pre_arm_mode.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_safe_mode.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_armed_manual.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_auto_engage.setStyleSheet(self.getDisabledButtonStyle())
        self.label_camera_video.clear()
        self.groupBox_algo.setEnabled(False)
        self.groupBox_algo.setStyleSheet(self.getDisabledPanelStyle())
        self.pushButton_algo_cv.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_algo_tf.setStyleSheet(self.getDisabledButtonStyle())
        self.scroll_log_to_last_line()
        self.groupBox_robot_action.hide()
        self.update_robot_action("")
        self.actionConfig.setEnabled(False)
        self.set_record_button_enabled(False)
        self.model.set_record_video(False)
    
    def enter_safe_mode(self):
        self.editText_target_order.clear()
        self.slide_up(self.groupBox_command_panel, Display.GROUPBOX_COMMAND_PANEL_HEIGHT)
        self.pushButton_armed_manual.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_auto_engage.setStyleSheet(self.getDisabledButtonStyle())
        self.groupBox_mode_control_panel.setStyleSheet(self.getPanelStyle())
        self.groupBox_mode_control_panel.setEnabled(True)
        self.groupBox_arm_mode.setStyleSheet(self.getDisabledPanelStyle())
        self.groupBox_arm_mode.setEnabled(False)
        self.pushButton_safe_mode.setStyleSheet(self.getSelectedButtonStyle())
        self.pushButton_safe_mode.setEnabled(False)
        self.groupBox_pre_arm_code.setStyleSheet(self.getGroupBoxStyle())
        self.groupBox_pre_arm_code.setEnabled(True)
        self.pushButton_pre_arm_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_pre_arm_mode.setEnabled(True)
        self.groupBox_algo.setEnabled(True)
        self.groupBox_algo.setStyleSheet(self.getPanelStyle())
        self.scroll_log_to_last_line()
        self.groupBox_robot_action.hide()
        self.update_robot_action("")
        self.actionConfig.setEnabled(False)
        self.set_record_button_enabled(False)
        self.model.set_record_video(False)
        
    def enter_pre_arm_mode(self):
        self.groupBox_arm_mode.setStyleSheet(self.getGroupBoxStyle())
        self.groupBox_arm_mode.setEnabled(True)
        self.pushButton_armed_manual.setStyleSheet(self.getButtonStyle())
        self.pushButton_armed_manual.setEnabled(True)
        self.pushButton_auto_engage.setStyleSheet(self.getButtonStyle())
        self.pushButton_auto_engage.setEnabled(True)
        self.pushButton_safe_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_safe_mode.setEnabled(True)
        self.editText_pre_arm_code.setText("")
        self.groupBox_pre_arm_code.setStyleSheet(self.getDisabledPanelStyle())
        self.groupBox_pre_arm_code.setEnabled(False)
        self.pushButton_pre_arm_mode.setStyleSheet(self.getSelectedButtonStyle())
        self.pushButton_auto_start.setChecked(False)
        self.pushButton_auto_start.setIcon(self.play_pause_icon)
        self.button_fire.hide()
        self.stackedWidget.setCurrentIndex(Display.COMMAND_WIDGET_MANUAL)
        self.stackedWidget.setFocus()
        self.checkbox_laser.hide()
        self.checkbox_cal.hide()
        self.groupBox_algo.setEnabled(False)
        self.groupBox_algo.setStyleSheet(self.getDisabledPanelStyle())
        self.slide_down(self.groupBox_command_panel, Display.GROUPBOX_COMMAND_PANEL_HEIGHT)
        self.scroll_log_to_last_line()
        self.groupBox_robot_action.hide()
        self.update_robot_action("")
        self.actionConfig.setEnabled(True)
        self.set_record_button_enabled(True)
    
    def enter_armed_manual_mode(self):
        self.pushButton_pre_arm_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_pre_arm_mode.setEnabled(True)
        self.pushButton_safe_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_armed_manual.setStyleSheet(self.getSelectedButtonStyle())
        self.pushButton_armed_manual.setEnabled(False)
        self.pushButton_auto_engage.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_auto_engage.setEnabled(False)
        self.stackedWidget.setCurrentIndex(Display.COMMAND_WIDGET_MANUAL)
        self.stackedWidget.setFocus()
        self.button_fire.show()
        self.checkbox_laser.show()
        self.checkbox_cal.show()
        self.pushButton_auto_engage.setEnabled(False)
        self.slide_down(self.groupBox_command_panel, Display.GROUPBOX_COMMAND_PANEL_HEIGHT)
        self.scroll_log_to_last_line()
        self.groupBox_robot_action.hide()
        self.update_robot_action("")
        self.actionConfig.setEnabled(False)
        
    def enter_auto_engage_mode(self):
        self.pushButton_pre_arm_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_pre_arm_mode.setEnabled(True)
        self.pushButton_safe_mode.setStyleSheet(self.getButtonStyle())
        self.pushButton_armed_manual.setStyleSheet(self.getDisabledButtonStyle())
        self.pushButton_armed_manual.setEnabled(False)
        self.pushButton_auto_engage.setStyleSheet(self.getSelectedButtonStyle())
        self.pushButton_auto_engage.setEnabled(False)
        self.stackedWidget.setCurrentIndex(Display.COMMAND_WIDGET_AUTO)
        self.stackedWidget.setFocus()
        self.slide_down(self.groupBox_command_panel, Display.GROUPBOX_COMMAND_PANEL_HEIGHT)
        self.scroll_log_to_last_line()
        self.groupBox_robot_action.show()
        self.actionConfig.setEnabled(False)
        
    def handle_key_event(self, key, pressed):
        currentState = self.model.get_system_state()
        if currentState == Setting.SYSTEM_MODE_AUTO_ENGAGE:
            return
        
        if currentState&Setting.SYSTEM_MODE_ARMED_MANUAL:
            self.model.key_pressed_signal.emit(key, pressed)
        elif currentState&Setting.SYSTEM_MODE_PRE_ARM:
            if key == Display.KEY_FIRE_1 or key == Display.KEY_FIRE_2:
                return
            self.model.key_pressed_signal.emit(key, pressed)
        
    def display_image(self, image):
        qimage = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(self.label_camera_video.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_camera_video.setPixmap(scaled_pixmap)
        
    def auto_engage_toggle(self):
        if self.pushButton_auto_start.isChecked():
            target_order_text = self.editText_target_order.text()
            if target_order_text == "":
                self.pushButton_auto_start.setChecked(False)
                return
            self.pushButton_auto_start.setIcon(self.pause_icon)
        else:
            self.pushButton_auto_start.setIcon(self.play_pause_icon)
            
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, Display.MENU_EXIT_DIALOG_TITLE, Display.MENU_EXIT_DIALOG_TEXT,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def pop_up_action_about(self):
        QtWidgets.QMessageBox.information(self, Display.MENU_ABOUT_DIALOG_TITLE, Display.MENU_ABOUT_DIALOG_TEXT)

    def pop_up_action_config(self):
        self.config_dialog.show()

    def update_laser_state(self, enabled):
        self.checkbox_laser.setChecked(enabled)
        
    def update_calibrate_state(self, enabled):
        self.checkbox_cal.setChecked(enabled)
        if enabled:
            self.button_fire.hide()
        else:
            self.button_fire.show()
            
    def update_algorithm(self, algo):
        if algo == Setting.CMD_USE_OPENCV:
            self.pushButton_algo_cv.setStyleSheet(self.getSelectedButtonStyle())
            self.pushButton_algo_tf.setStyleSheet(self.getButtonStyle())
        elif algo == Setting.CMD_USE_TF:
            self.pushButton_algo_cv.setStyleSheet(self.getButtonStyle())
            self.pushButton_algo_tf.setStyleSheet(self.getSelectedButtonStyle())
        
    def algo_button_clicked(self):
        sender = self.sender()
        algoText = sender.text()
        if algoText == Display.BUTTON_OPEN_CV_TITLE:
            self.pushButton_algo_cv.setStyleSheet(self.getSelectedButtonStyle())
            self.pushButton_algo_tf.setStyleSheet(self.getButtonStyle())
        else:
            self.pushButton_algo_cv.setStyleSheet(self.getButtonStyle())
            self.pushButton_algo_tf.setStyleSheet(self.getSelectedButtonStyle())
    
    def update_robot_action(self, text):
        self.nonEdit_robot_action.setText(text)
    
    def display_alert(self, text):
        global messageBox
        if messageBox is None:
            messageBox = QtWidgets.QMessageBox(self)
            messageBox.setIcon(QtWidgets.QMessageBox.Warning)
            messageBox.setWindowTitle(Display.ALERT_DIALOG_TITLE)
            messageBox.show()
        messageBox.setText(text)
        messageBox.show()
        
    def on_record_clicked(self):
        if self.recordMovie.state() == QMovie.Running:
            self.recordMovie.stop()
            self.recordMovie.jumpToFrame(0)
            self.iconLabel.hide()
            self.model.set_record_video(False)
        else:
            self.recordMovie.start()
            self.iconLabel.show()
            self.model.set_record_video(True)

    def on_play_clicked(self):
        if self.playMovie.state() == QMovie.Running:
            self.playMovie.stop()
            self.playMovie.jumpToFrame(0)
        else:
            self.playMovie.start()
            self.video_player.show()
            
    def set_record_button_enabled(self, enabled):
        self.pushButton_record.setEnabled(enabled)
        if enabled:
            self.gifRecordLabel.setMovie(self.recordMovie)
            self.recordMovie.start()
            self.recordMovie.jumpToFrame(0)
            self.recordMovie.stop()
        else:
            self.gifRecordLabel.setMovie(self.recordMovieDisabled)
            self.recordMovieDisabled.start()
            self.recordMovieDisabled.jumpToFrame(0)
            self.recordMovieDisabled.stop()
            self.iconLabel.hide()
            
    def closeVideoPlayer(self):
        self.playMovie.stop()
        self.playMovie.jumpToFrame(0)