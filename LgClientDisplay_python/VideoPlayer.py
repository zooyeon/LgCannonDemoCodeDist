import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, 
                             QProgressBar, QDialog, QSizePolicy)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, QtGui

from constant.DisplayConstant import DIALOG_VIDEO_FILE_LOCATION, FONT_FAMILY
from constant.StyleSheet import LABEL_CAMERA_STYLE, VIDEO_PLAYER_PROGRESS_STYLE

class VideoPlayer(QDialog):
    def __init__(self, closeCallback):
        super(VideoPlayer, self).__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)
        
        self.label_camera_video = QLabel(self)
        self.label_camera_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_camera_video.setStyleSheet(LABEL_CAMERA_STYLE)
        self.label_camera_video.setAlignment(QtCore.Qt.AlignCenter)
        self.closeCallbackFunc = closeCallback
        
        self.find_button = QPushButton("Find File", self)
        self.left_button = QPushButton("<< 5s", self)
        self.play_pause_button = QPushButton("Play", self)
        self.stop_button = QPushButton("Stop", self)
        self.right_button = QPushButton("5s >>", self)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet(VIDEO_PLAYER_PROGRESS_STYLE)
        self.progress_bar.setFixedHeight(25)
        self.time_label = QLabel("00:00:00 / 00:00:00", self)
        
        self.init_ui()
        
        self.find_button.clicked.connect(self.open_file)
        self.left_button.clicked.connect(lambda: self.seek_video(-5))
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop_playback)
        self.right_button.clicked.connect(lambda: self.seek_video(5))
        
        self.video_file = DIALOG_VIDEO_FILE_LOCATION
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.playing = False
        self.frame_rate = 30
        self.current_frame = 0
        self.total_frames = 0
        
    def init_ui(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.right_button)

        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.time_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setFamily(FONT_FAMILY)
        font.setBold(True)
        self.time_label.setFont(font)
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.time_label)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_camera_video)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(button_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0)
        main_layout.setStretch(2, 0)
        
        self.setLayout(main_layout)
        
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.avi *.mp4 *.mkv)")
        if file_name:
            self.video_file = file_name
            self.cap = cv2.VideoCapture(self.video_file)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.update_progress_bar()
            self.stop_playback()
            self.play_pause_button.setText("Play")

    def update_progress_bar(self):
        self.progress_bar.setMaximum(self.total_frames)
        self.progress_bar.setValue(self.current_frame)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        total_duration = self.total_frames / self.frame_rate
        current_duration = self.current_frame / self.frame_rate
        self.time_label.setText(f"{self.format_time(current_duration)} / {self.format_time(total_duration)}")
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)

    def format_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"

    def seek_video(self, seconds):
        if self.cap:
            self.current_frame = max(0, min(self.total_frames, self.current_frame + int(seconds * self.frame_rate)))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.update_progress_bar()
            self.show_frame()

    def toggle_play_pause(self):
        if self.playing:
            self.pause_video()
        else:
            self.play_video()

    def play_video(self):
        if self.cap:
            self.playing = True
            self.timer.start(1000 // self.frame_rate)
            self.play_pause_button.setText("Pause")

    def pause_video(self):
        if self.playing:
            self.playing = False
            self.timer.stop()
            self.play_pause_button.setText("Play")

    def stop_playback(self):
        if self.cap:
            self.playing = False
            self.timer.stop()
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.update_progress_bar()
            self.show_frame()
            self.play_pause_button.setText("Play")

    def next_frame(self):
        if self.cap and self.playing:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame += 1
                self.update_progress_bar()
                self.display_frame(frame)
            else:
                self.stop_playback()

    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], frame_rgb.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label_camera_video.setPixmap(pixmap)

    def show_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
    
    def closeEvent(self, event):
        event.accept()
        self.closeCallbackFunc()
        