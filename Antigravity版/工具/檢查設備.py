#!/usr/bin/env python3
"""只讀設備檢查；不安裝軟體、不下載模型、不輸出機密。"""
import importlib.util
import os
from pathlib import Path
import shutil
import sys

def show(name, value):
    print(f"{name}：{value}")

show("Python", sys.version.split()[0])
for cmd in ("ffmpeg", "ffprobe", "node"):
    show(cmd, shutil.which(cmd) or "未在 PATH 找到")
show("Pillow", "已安裝" if importlib.util.find_spec("PIL") else "未在目前 Python 環境找到")
if importlib.util.find_spec("imageio_ffmpeg"):
    import imageio_ffmpeg
    show("工作區 FFmpeg", imageio_ffmpeg.get_ffmpeg_exe())
else:
    show("工作區 FFmpeg", "未安裝；可使用系統 FFmpeg")
show("mutagen", "已安裝" if importlib.util.find_spec("mutagen") else "未找到；線上旁白需要")
show("edge-tts", "已安裝" if importlib.util.find_spec("edge_tts") else "未在目前 Python 環境找到；僅旁白示範需要")
show("faster-whisper", "已安裝" if importlib.util.find_spec("faster_whisper") else "未找到；僅錄音字幕轉錄需要")
windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
fonts = [windir / "Fonts" / "msjhbd.ttc", windir / "Fonts" / "msjh.ttc"]
available = next((str(p) for p in fonts if p.exists()), "未在預設位置找到微軟正黑體；可在指令指定中文字型")
show("繁中文字型", available)
try:
    usage = shutil.disk_usage(Path.cwd())
    show("目前磁碟可用空間", f"{usage.free / 1024**3:.1f} GiB")
except OSError:
    show("磁碟空間", "無法讀取")
show("GPU", "本示範使用 CPU libx264；不以獨立顯示卡為必要條件")
print("\n以上只是初步檢查，不代表能在限時內完成；必須實際輸出與檢查短片。")
