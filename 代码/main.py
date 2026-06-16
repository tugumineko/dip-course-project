"""老照片修复与增强馆 -- 程序入口。

运行:
    E:\\miniconda3\\envs\\ai-service\\python.exe main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import App

if __name__ == "__main__":
    App().run()
