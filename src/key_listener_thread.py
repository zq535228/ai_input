from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard

class KeyListenerThread(QThread):
    option_pressed = pyqtSignal()
    option_released = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        def on_press(key):
            self.main_window.setWindowOpacity(0.8)
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed.emit()
        def on_release(key):
            self.main_window.setWindowOpacity(0.3)
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_released.emit()
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join() 