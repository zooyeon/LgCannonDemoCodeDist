from PyQt5 import QtWidgets, QtCore

from constant.DisplayConstant import BUTTON_CV_AREA1_OBJECT_NAME, BUTTON_CV_AREA2_OBJECT_NAME, BUTTON_CV_AREA_MAX_OBJECT_NAME, BUTTON_CV_AREA_MIN_OBJECT_NAME, BUTTON_CV_THRESHOLD_OBJECT_NAME, BUTTON_OFF, BUTTON_ON, BUTTON_SET, BUTTON_TF_DY_MV_OFF_OBJECT_NAME, BUTTON_TF_DY_MV_ON_OBJECT_NAME, BUTTON_TF_EPSILON_OBJECT_NAME, BUTTON_TF_T1_OBJECT_NAME, BUTTON_TF_BOX_OBJECT_NAME, DIALOG_TITLE, GROUP_BOX_OPEN_CV, GROUP_BOX_TENSOR_FLOW, LABLE_OPEN_CV_AREA1, LABLE_OPEN_CV_AREA2, LABLE_OPEN_CV_AREA_MAX, LABLE_OPEN_CV_AREA_MIN, LABLE_OPEN_CV_THRESHOLD, LABLE_TENSOR_FLOW_DYNAMIC, LABLE_TENSOR_FLOW_EPSILON, LABLE_TENSOR_FLOW_SCORE, \
                                        LABLE_TENSOR_FLOW_BOX
from constant.StyleSheet import BUTTON_DISABLED_STYLE, BUTTON_SELECTED_STYLE, BUTTON_STYLE

class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setWindowTitle(DIALOG_TITLE)
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # OpenCv group box
        self.groupBox_cv = QtWidgets.QGroupBox(GROUP_BOX_OPEN_CV, self)
        self.groupBox_cv_layout = QtWidgets.QVBoxLayout(self.groupBox_cv)
        
        # Threashold
        self.cv_threshold_layout = QtWidgets.QHBoxLayout()
        self.label_cv_threshold = QtWidgets.QLabel(LABLE_OPEN_CV_THRESHOLD, self.groupBox_cv)
        self.cv_threshold_layout.addWidget(self.label_cv_threshold)
        
        self.editText_open_cv_threshold = QtWidgets.QLineEdit(self.groupBox_cv)
        self.cv_threshold_layout.addWidget(self.editText_open_cv_threshold)
        
        self.button_set_cv_threshold = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_cv)
        self.button_set_cv_threshold.setObjectName(BUTTON_CV_THRESHOLD_OBJECT_NAME)
        self.cv_threshold_layout.addWidget(self.button_set_cv_threshold)
        
        self.groupBox_cv_layout.addLayout(self.cv_threshold_layout)
        
        # Area1
        self.cv_area1_layout = QtWidgets.QHBoxLayout()
        self.label_cv_area1 = QtWidgets.QLabel(LABLE_OPEN_CV_AREA1, self.groupBox_cv)
        self.cv_area1_layout.addWidget(self.label_cv_area1)
        
        self.editText_open_cv_area1 = QtWidgets.QLineEdit(self.groupBox_cv)
        self.cv_area1_layout.addWidget(self.editText_open_cv_area1)
        
        self.button_set_cv_area1 = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_cv)
        self.button_set_cv_area1.setObjectName(BUTTON_CV_AREA1_OBJECT_NAME)
        self.cv_area1_layout.addWidget(self.button_set_cv_area1)
        
        self.groupBox_cv_layout.addLayout(self.cv_area1_layout)
        
        # Area2
        self.cv_area2_layout = QtWidgets.QHBoxLayout()
        self.label_cv_area2 = QtWidgets.QLabel(LABLE_OPEN_CV_AREA2, self.groupBox_cv)
        self.cv_area2_layout.addWidget(self.label_cv_area2)
        
        self.editText_open_cv_area2 = QtWidgets.QLineEdit(self.groupBox_cv)
        self.cv_area2_layout.addWidget(self.editText_open_cv_area2)
        
        self.button_set_cv_area2 = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_cv)
        self.button_set_cv_area2.setObjectName(BUTTON_CV_AREA2_OBJECT_NAME)
        self.cv_area2_layout.addWidget(self.button_set_cv_area2)
        
        self.groupBox_cv_layout.addLayout(self.cv_area2_layout)
        
        self.layout.addWidget(self.groupBox_cv)
        
        # cv_area_min
        self.cv_area_min_layout = QtWidgets.QHBoxLayout()
        self.label_cv_area_min = QtWidgets.QLabel(LABLE_OPEN_CV_AREA_MIN, self.groupBox_cv)
        self.cv_area_min_layout.addWidget(self.label_cv_area_min)
        
        self.editText_open_cv_area_min = QtWidgets.QLineEdit(self.groupBox_cv)
        self.cv_area_min_layout.addWidget(self.editText_open_cv_area_min)
        
        self.button_set_cv_area_min = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_cv)
        self.button_set_cv_area_min.setObjectName(BUTTON_CV_AREA_MIN_OBJECT_NAME)
        self.cv_area_min_layout.addWidget(self.button_set_cv_area_min)
        
        self.groupBox_cv_layout.addLayout(self.cv_area_min_layout)
        
        # cv_area_max
        self.cv_area_max_layout = QtWidgets.QHBoxLayout()
        self.label_cv_area_max = QtWidgets.QLabel(LABLE_OPEN_CV_AREA_MAX, self.groupBox_cv)
        self.cv_area_max_layout.addWidget(self.label_cv_area_max)
        
        self.editText_open_cv_area_max = QtWidgets.QLineEdit(self.groupBox_cv)
        self.cv_area_max_layout.addWidget(self.editText_open_cv_area_max)
        
        self.button_set_cv_area_max = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_cv)
        self.button_set_cv_area_max.setObjectName(BUTTON_CV_AREA_MAX_OBJECT_NAME)
        self.cv_area_max_layout.addWidget(self.button_set_cv_area_max)
        
        self.groupBox_cv_layout.addLayout(self.cv_area_max_layout)
        
        # TensorFlow group box
        self.groupBox_tf = QtWidgets.QGroupBox(GROUP_BOX_TENSOR_FLOW, self)
        self.groupBox_tf_layout = QtWidgets.QVBoxLayout(self.groupBox_tf)
        
        # Score
        self.tf_score_layout = QtWidgets.QHBoxLayout()
        self.label_tf_score = QtWidgets.QLabel(LABLE_TENSOR_FLOW_SCORE, self.groupBox_tf)
        self.tf_score_layout.addWidget(self.label_tf_score)
        
        self.editText_tf_score = QtWidgets.QLineEdit(self.groupBox_tf)
        self.tf_score_layout.addWidget(self.editText_tf_score)
        
        self.button_set_tf_score = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_tf)
        self.button_set_tf_score.setObjectName(BUTTON_TF_T1_OBJECT_NAME)
        self.tf_score_layout.addWidget(self.button_set_tf_score)
        
        self.groupBox_tf_layout.addLayout(self.tf_score_layout)
        
        # Box
        self.tf_box_layout = QtWidgets.QHBoxLayout()
        self.label_tf_box = QtWidgets.QLabel(LABLE_TENSOR_FLOW_BOX, self.groupBox_tf)
        self.tf_box_layout.addWidget(self.label_tf_box)
        
        self.editText_tf_box = QtWidgets.QLineEdit(self.groupBox_tf)
        self.tf_box_layout.addWidget(self.editText_tf_box)
        
        self.button_set_tf_box = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_tf)
        self.button_set_tf_box.setObjectName(BUTTON_TF_BOX_OBJECT_NAME)
        self.tf_box_layout.addWidget(self.button_set_tf_box)
        
        self.groupBox_tf_layout.addLayout(self.tf_box_layout)
        
        # TF_EPSILON
        self.tf_epsilon_layout = QtWidgets.QHBoxLayout()
        self.label_tf_epsilon = QtWidgets.QLabel(LABLE_TENSOR_FLOW_EPSILON, self.groupBox_tf)
        self.tf_epsilon_layout.addWidget(self.label_tf_epsilon)
        
        self.editText_tf_epsilon = QtWidgets.QLineEdit(self.groupBox_tf)
        self.tf_epsilon_layout.addWidget(self.editText_tf_epsilon)
        
        self.button_set_tf_epsilon = QtWidgets.QPushButton(BUTTON_SET, self.groupBox_tf)
        self.button_set_tf_epsilon.setObjectName(BUTTON_TF_EPSILON_OBJECT_NAME)
        self.tf_epsilon_layout.addWidget(self.button_set_tf_epsilon)
        
        self.groupBox_tf_layout.addLayout(self.tf_epsilon_layout)
        
        # Dynamic Move
        self.tf_dy_mv_layout = QtWidgets.QHBoxLayout()
        self.label_tf_dy_mv = QtWidgets.QLabel(LABLE_TENSOR_FLOW_DYNAMIC, self.groupBox_tf)
        self.tf_dy_mv_layout.addWidget(self.label_tf_dy_mv)
        
        self.button_dy_mv_on = QtWidgets.QPushButton(BUTTON_ON, self.groupBox_tf)
        self.button_dy_mv_on.setObjectName(BUTTON_TF_DY_MV_ON_OBJECT_NAME)
        self.button_dy_mv_on.setCheckable(True)
        self.button_dy_mv_on.clicked.connect(self.toggle_tf_dy_mv)
        self.button_dy_mv_on.setStyleSheet(BUTTON_STYLE)
        self.button_dy_mv_off = QtWidgets.QPushButton(BUTTON_OFF, self.groupBox_tf)
        self.button_dy_mv_off.setObjectName(BUTTON_TF_DY_MV_OFF_OBJECT_NAME)
        self.button_dy_mv_off.setCheckable(True)
        self.button_dy_mv_off.clicked.connect(self.toggle_tf_dy_mv)
        self.button_dy_mv_off.setStyleSheet(BUTTON_STYLE)
        self.tf_dy_mv_layout.addWidget(self.button_dy_mv_on)
        self.tf_dy_mv_layout.addWidget(self.button_dy_mv_off)
        
        self.groupBox_tf_layout.addLayout(self.tf_dy_mv_layout)
        
        self.layout.addWidget(self.groupBox_tf)
        
    def toggle_tf_dy_mv(self):
        if self.button_dy_mv_on.isChecked():
            self.button_dy_mv_on.setCheckable(False)
            self.button_dy_mv_on.setStyleSheet(BUTTON_SELECTED_STYLE)
            self.button_dy_mv_off.setCheckable(True)
            self.button_dy_mv_off.setChecked(False)
            self.button_dy_mv_off.setStyleSheet(BUTTON_DISABLED_STYLE)
        elif self.button_dy_mv_off.isChecked():
            self.button_dy_mv_on.setCheckable(True)
            self.button_dy_mv_on.setChecked(False)
            self.button_dy_mv_on.setStyleSheet(BUTTON_DISABLED_STYLE)
            self.button_dy_mv_off.setCheckable(False)
            self.button_dy_mv_off.setStyleSheet(BUTTON_SELECTED_STYLE)