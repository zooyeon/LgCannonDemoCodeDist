import socket
import threading
import struct
import time
import cv2
import numpy as np
import constant.NetworkConfig as Network
import constant.SettingConstant as Setting

class TcpSendReceiver:
    def __init__(self, host, port, connection_callback, image_callback, text_callback, state_callback, command_callback):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.stop_event = threading.Event()
        self.recv_thread = None
        self.connection_callback = connection_callback
        self.image_callback = image_callback
        self.text_callback = text_callback
        self.state_callback = state_callback
        self.command_callback = command_callback

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.client_socket.settimeout(3)
        try:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.settimeout(None)
            self.connected = True
            self.recv_thread = threading.Thread(target=self.recv_data)
            self.recv_thread.start()
            self.connection_callback(Network.NETWORK_CONNECTED)
        except socket.error as e:
            self.disconnect()
            
        return self.connected

    def disconnect(self):
        self.connected = False
        self.stop_event.set()
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        if self.state_callback:
            self.state_callback(Setting.SYSTEM_MODE_UNKNOWN)
        if self.connection_callback:
            self.connection_callback(Network.NETWORK_DISCONNECTED)
        self.image_callback = None
        self.text_callback = None
        self.state_callback = None
        if self.recv_thread is not None:
            try:
                self.recv_thread.join()
            except RuntimeError as e:
                print(f"Error joining thread: {e}")
            except Exception as e:
                print(f"Unexpected error joining thread: {e}")

    def send_message(self, msg_type, msg_data):
        if not self.connected:
            return
        msg_len = len(msg_data)
        msg_header = struct.pack('!II', msg_len, msg_type)
        message = msg_header + msg_data

        total_sent = 0
        while total_sent < len(message):
            try:
                sent = self.client_socket.send(message[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
            except socket.error as e:
                if e.errno == socket.EWOULDBLOCK:
                    time.sleep(0.01)
                else:
                    self.disconnect()
                    break

    def recv_data(self):
        while not self.stop_event.is_set():
            try:
                msg_header = self.client_socket.recv(8)
                if len(msg_header) < 8:
                    self.disconnect()
                    break

                msg_len, msg_type = struct.unpack('!II', msg_header)
                msg_data = b""
                while len(msg_data) < msg_len:
                    if self.client_socket is not None:
                        chunk = self.client_socket.recv(msg_len - len(msg_data))
                    else:
                        self.disconnect()
                        print("Socket is not connected, cannot receive data")
                        return
                    if not chunk:
                        self.disconnect()
                        break
                    msg_data += chunk

                if msg_type == Network.MT_STATE:
                    self.process_state(msg_data)
                elif msg_type == Network.MT_IMAGE:
                    self.process_image(msg_data)
                elif msg_type == Network.MT_TEXT:
                    self.process_text(msg_data)
                elif msg_type == Network.MT_COMMANDS:
                    self.process_command(msg_data)

            except socket.error as e:
                self.disconnect()
                break

    def process_state(self, state_data):
        self.state_callback(int.from_bytes(state_data, byteorder='big'))

    def process_image(self, img_data):
        np_arr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        last_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if image is not None and self.image_callback:
            self.image_callback(last_image)

    def process_text(self, text_data):
        self.text_callback(text_data.decode())
        
    def process_command(self, cmd):
        self.command_callback(int.from_bytes(cmd, byteorder='big'))

    def is_connected(self):
        return self.connected

    def send_state_change_request_to_server(self, state):
        if self.is_connected():
            msg_type = Network.MT_STATE_CHANGE_REQ
            msg_data = struct.pack('>I', state)
            self.send_message(msg_type, msg_data)
            return True
        return False

    def send_prearm_code_to_server(self, code):
        if self.is_connected():
            msg_type = Network.MT_PREARM
            msg_data = code.encode() + b'\0'
            self.send_message(msg_type, msg_data)
            return True
        return False

    def send_command_to_server(self, code):
        if self.is_connected():
            msg_type = Network.MT_COMMANDS
            msg_data = struct.pack('B', code)
            self.send_message(msg_type, msg_data)
            return True
        return False

    def send_calib_to_server(self, code):
        if self.is_connected():
            msg_type = Network.MT_CALIB_COMMANDS
            msg_data = struct.pack('B', code)
            self.send_message(msg_type, msg_data)
            return True
        return False

    def send_target_order_to_server(self, target_order):
        if self.is_connected():
            msg_type = Network.MT_TARGET_SEQUENCE
            msg_data = target_order.encode() + b'\0'
            self.send_message(msg_type, msg_data)
            return True
        return False
    
    def send_config_to_server(self, type, value):
        if self.is_connected():
            msg_type = Network.MT_CONFIG
            strValue = f"{type}:{value}"
            msg_data = strValue.encode('ascii') + b'\0'
            self.send_message(msg_type, msg_data)
            return True
        return False