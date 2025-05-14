import keyboard

def on_alt_down(e):
    print("Alt(Option) 键被按下")

def on_alt_up(e):
    print("Alt(Option) 键被释放")

keyboard.on_press_key('alt', on_alt_down)
keyboard.on_release_key('alt', on_alt_up)

keyboard.wait()  # 保持程序运行