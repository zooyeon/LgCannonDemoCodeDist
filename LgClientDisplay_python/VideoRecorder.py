import os
from PyQt5 import QtCore
import queue
import cv2
from datetime import datetime
from constant.DisplayConstant import DIALOG_VIDEO_FILE_LOCATION

class VideoRecorder(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.event_queue_record = queue.Queue()
        self.recording = False
        self.video_writer = None
        
        self.directory = os.path.join(os.getcwd(), DIALOG_VIDEO_FILE_LOCATION)
        self.ensure_directory_exists(self.directory)
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        
        self.start()

        self.event_queue_record.put(None)
        self.wait()

    def run(self):
        while True:
            event = self.event_queue_record.get()
            if event is None:
                break
            func, args = event
            func(*args)
            self.event_queue_record.task_done()
    
    def set_recording(self, record, frame_size):
        self.recording = record
        if record and self.video_writer is None:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.video_file = os.path.join(self.directory, f"video_{current_time}.avi")
            self.video_writer = cv2.VideoWriter(self.video_file, self.fourcc, 35.0, frame_size)
    
    def get_recording(self):
        return self.recording
    
    # Queue Function
    def enqueue_record_video(self, image):
        self.event_queue_record.put((self.start_recording, [image]))

    def enqueue_stop_record_video(self):
        self.event_queue_record.put((self.stop_recording, []))
    
    def ensure_directory_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def start_recording(self, image):
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if self.video_writer is not None:
            print("Writing video")
            self.video_writer.write(frame)

    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.video_file = None