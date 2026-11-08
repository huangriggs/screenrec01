"""工作區內自備 FFmpeg 的定位，失敗才退回現有系統工具。"""
import shutil

def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError, OSError):
        return shutil.which('ffmpeg')
