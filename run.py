
import sys
import os
import subprocess


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def main():

    # enter the directory like this:
    with cd("C:\\Program Files\\Aimsun\\Aimsun Next 8.4"):
        subprocess.call("aconsole.exe -script C:\\Users\\ahmadiam\\Desktop\\main.py C:\\Users\\ahmadiam\\Desktop\\Sample\\OCR_MS_20323e.ang")


if __name__ == '__main__':
        main()









