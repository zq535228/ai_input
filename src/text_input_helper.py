import platform
from PyQt5.QtCore import QThread
from pynput import keyboard

class TextInputHelper:
    @staticmethod
    def type_text(text, clipboard, keyboard_controller, append_log, auto_send=False):
        """使用剪贴板进行文本输入"""
        append_log(f"使用剪贴板进行文本输入: {text}")
        try:
            # 使用剪贴板输入文本
            success = TextInputHelper.paste_text_windows(text, clipboard, keyboard_controller, append_log, auto_send)
            if not success:
                raise Exception("文本输入失败")
            append_log("文本输入完成")
        except Exception as e:
            append_log(f"模拟输入失败: {str(e)}")
            print(f"识别结果: {text}")

    @staticmethod
    def paste_text_windows(text, clipboard, keyboard_controller, append_log, auto_send=False):
        """使用剪贴板和快捷键模拟文本输入"""
        try:
            append_log(f"准备输入文本: {text}")
            # 保存当前剪贴板内容
            old_clipboard = clipboard.text()
            # 将文本复制到剪贴板
            clipboard.setText(text)
            # 模拟粘贴操作
            if platform.system() == 'Darwin':  # macOS
                with keyboard_controller.pressed(keyboard.Key.cmd):
                    keyboard_controller.tap('v')
                append_log("macOS粘贴操作完成: " + text)
            else:  # Windows/Linux
                with keyboard_controller.pressed(keyboard.Key.ctrl):
                    keyboard_controller.tap('v')
                append_log("Windows/Linux粘贴操作完成: " + text)
            QThread.msleep(50)  # 给一点时间让粘贴操作完成
            
            # 如果启用了自动发送，模拟按下回车键
            if auto_send:
                QThread.msleep(50)  # 给一点额外时间确保文本已经粘贴完成
                keyboard_controller.tap(keyboard.Key.enter)
                append_log("自动发送：已按下回车键")
            
            return True
        except Exception as e:
            append_log(f"文本输入失败: {str(e)}")
            return False 