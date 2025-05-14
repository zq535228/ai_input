#!/bin/bash

# 1. 打包
pyinstaller --name "检验大叔AI语音输入法" --windowed main.py --icon src/voice-input.icns --add-data "src/voice-input.png:."

# 2. 添加麦克风权限声明到 Info.plist
PLIST="dist/检验大叔AI语音输入法.app/Contents/Info.plist"
KEY="NSMicrophoneUsageDescription"
VALUE="需要使用麦克风进行语音输入"

# 先尝试修改（如果已存在），否则添加
/usr/libexec/PlistBuddy -c "Set :$KEY '$VALUE'" "$PLIST" 2>/dev/null \
|| /usr/libexec/PlistBuddy -c "Add :$KEY string '$VALUE'" "$PLIST"

# 3. 添加 AppleEvents 权限声明
KEY2="NSAppleEventsUsageDescription"
VALUE2="需要用于全局快捷键监听"
/usr/libexec/PlistBuddy -c "Set :$KEY2 '$VALUE2'" "$PLIST" 2>/dev/null \
|| /usr/libexec/PlistBuddy -c "Add :$KEY2 string '$VALUE2'" "$PLIST"

# 4. 添加辅助功能权限
KEY3="NSAccessibility"
VALUE3="YES"
/usr/libexec/PlistBuddy -c "Set :$KEY3 $VALUE3" "$PLIST" 2>/dev/null \
|| /usr/libexec/PlistBuddy -c "Add :$KEY3 bool $VALUE3" "$PLIST"

echo "打包完成，并已自动添加麦克风权限声明到 Info.plist"