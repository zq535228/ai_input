from PyQt5.QtCore import QThread, pyqtSignal
import json
import pycurl
from io import BytesIO
import logging
import os
logger = logging.getLogger(__name__)

class SpeechRecognizerThread(QThread):
    message = pyqtSignal(str)
    textRecognized = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.api_key = "pat_4khONpfnuKZ8ZZ7puV1jy7gkYkblUxigpvDrGdPPST6k2MRoPQTqbtqfouRpAYZA"
        self._running = True

    def run(self):
        if not self._running:
            return

        url = "https://api.coze.cn/v1/audio/transcriptions"
        buffer = BytesIO()
        c = pycurl.Curl()
        try:
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.HTTPHEADER, [f"Authorization: Bearer {self.api_key}"])
            c.setopt(c.HTTPPOST, [("file", (c.FORM_FILE, self.filename))])
            c.perform()
            # 获取响应状态码
            response_code = c.getinfo(c.RESPONSE_CODE)
            # 获取响应内容
            response_body = buffer.getvalue().decode('utf-8')

            if response_code == 200:
                result = json.loads(response_body)
                if result.get('code') == 0 and 'data' in result:
                    self.textRecognized.emit(result['data']['text'])
                    # 删除文件
                    self.message.emit(f"声音文件: {self.filename}")
                    # os.remove(self.filename)
                else:
                    self.message.emit(f"API返回错误: {result.get('msg', '未知错误')}")
            else:
                self.message.emit(f"API调用失败: {response_code}")
        except Exception as e:
            self.message.emit(f"识别线程发生错误: {str(e)}")
        finally:
            c.close()

    def stop(self):
        self._running = False

    def _emit_error(self, msg):
        logger.error(msg)
        self.errorOccurred.emit(msg) 