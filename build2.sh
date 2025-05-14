#!/bin/bash

# 1. 打包
pyinstaller --name "检验大叔AI语音输入法" --onefile main.py --icon src/voice-input.icns --add-data "src/voice-input.png:."


echo "打包完成，并已自动添加麦克风权限声明到 Info.plist"