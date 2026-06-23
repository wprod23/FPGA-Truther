from ctypes import windll

def ignore_auto_scaling():
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass