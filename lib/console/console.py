import os

def clear_console():
    # 'nt' is for Windows, 'posix' is for macOS and Linux
    os.system('cls' if os.name == 'nt' else 'clear')

red = "\033[31m"
green = "\033[32m"
blue = "\033[34m"
clear = "\033[0m"