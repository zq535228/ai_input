import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pynput import keyboard
from src.speech_recognizer_thread import SpeechRecognizerThread
import time
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from PyQt5.QtCore import QTimer
import platform
import logging
from src.text_input_helper import TextInputHelper
from src.key_listener_thread import KeyListenerThread
from PyQt5.QtGui import QIcon
import os
import tempfile


logger = logging.getLogger(__name__)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(".")+"/src/", relative_path)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('检验大叔AI语音输入')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        # self.setWindowOpacity(0.8)
        self.textarea = QTextEdit(self)
        self.textarea.setReadOnly(True)
        self.textarea.setText('欢迎使用语音识别与录音工具！\n按住 Option (⌥) 键开始录音，松开后自动识别输入。')
        
        # 添加自动发送复选框
        self.auto_send_checkbox = QCheckBox('自动发送', self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.auto_send_checkbox)
        layout.addWidget(self.textarea)
        self.setLayout(layout)

        self.keyboard_controller = keyboard.Controller()

        self.listener_thread = KeyListenerThread(self)
        self.listener_thread.option_pressed.connect(self.on_option_pressed)
        self.listener_thread.option_released.connect(self.on_option_released)
        self.listener_thread.start()

        self.speech_recognizer = None
        self.fs = 44100  # 采样率
        self.recording = []
        self.is_recording = False

        self.init_tray()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path('voice-input.png')))
        self.tray_icon.setToolTip('检验大叔AI语音输入')
        
        show_action = QAction('显示主窗口', self)
        quit_action = QAction('退出', self)
        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def append_log(self, text):
        self.textarea.append(text)

    def on_option_pressed(self):
        self.append_log('Option (⌥) 键已按下，开始录音...')
        # self.append_log(f'任务开始执行')
        # 录音开始
        self.is_recording = True
        self.recording = []
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)
        self.stream.start()

    def on_option_released(self):
        try:
            filename = None
            self.append_log('Option (⌥) 键已释放，结束录音...')
            # 录音结束
            if self.is_recording:
                self.is_recording = False
                self.stream.stop()
                self.stream.close()
                if len(self.recording) > 0:
                    audio_data = np.concatenate(self.recording, axis=0)
                    # 保存到临时目录
                    filename = os.path.join(tempfile.gettempdir(), f"record_{int(time.time())}.wav")
                    write(filename, self.fs, audio_data)
                else:
                    self.append_log('未检测到录音数据')
            if self.speech_recognizer is not None and self.speech_recognizer.isRunning():
                self.speech_recognizer.stop()
                self.speech_recognizer.wait()  # 等待上一个线程安全退出
            if filename is not None:
                self.speech_recognizer = SpeechRecognizerThread(filename)
                self.speech_recognizer.textRecognized.connect(self.on_task_finished)
                self.speech_recognizer.errorOccurred.connect(self.on_error)
                self.speech_recognizer.message.connect(self.append_log)
                self.speech_recognizer.start()
                self.append_log(f'声音识别执行中...')
            else:
                self.append_log(f'没有录音文件, 无法执行任务')
        except Exception as e:
            import traceback
            self.append_log(f'崩溃异常: {e}\n{traceback.format_exc()}')

    def on_task_finished(self, name):
        # self.append_log(f'{name} 任务处理完成')
        QTimer.singleShot(500, lambda: self.append_log(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: {name}'))
        self.type_text(name)

    def on_error(self, error):
        self.append_log(f'错误: {error}')

    def type_text(self, text):
        TextInputHelper.type_text(
            text, 
            QApplication.clipboard(), 
            self.keyboard_controller, 
            self.append_log,
            self.auto_send_checkbox.isChecked()
        )

    def audio_callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.recording.append(indata.copy())

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("voice-input.png")
    tray = QSystemTrayIcon(QIcon(icon_path), app)
    tray.show()
    sys.exit(app.exec_())
