from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from 環境工具 import find_ffmpeg


def check_x264(ffmpeg: str | None) -> bool:
    if not ffmpeg:
        return False
    try:
        run = subprocess.run([ffmpeg, '-hide_banner', '-encoders'], capture_output=True, text=True, timeout=15, errors='replace')
        return run.returncode == 0 and 'libx264' in run.stdout
    except (OSError, subprocess.SubprocessError):
        return False


def main() -> int:
    ffmpeg = find_ffmpeg()
    fonts = [Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts' / n for n in ('msjh.ttc', 'msjhbd.ttc', 'mingliu.ttc')]
    installed_fonts = [str(p) for p in fonts if p.is_file()]
    usage = shutil.disk_usage(Path.cwd())
    data = {
        'python': sys.version.split()[0], 'python_path': sys.executable,
        'cpu_logical_threads': os.cpu_count(), 'gpu': '不要求；本檢查不偵測或停用 GPU',
        'pillow': importlib.util.find_spec('PIL') is not None,
        'ffmpeg': ffmpeg, 'ffmpeg_libx264': check_x264(ffmpeg),
        'windows_chinese_fonts': installed_fonts,
        'free_disk_gib': round(usage.free / 1024**3, 2),
        'node_optional': shutil.which('node'),
        'edge_tts_optional': importlib.util.find_spec('edge_tts') is not None,
        'not_tested': ['Codex 帳號與網路', 'Concat MCP 連線', 'Whisper 模型', '字幕正確性', '實際編碼與播放'],
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    ready = bool(data['pillow'] and data['ffmpeg_libx264'] and installed_fonts)
    print('CPU 靜音範例基本依賴：' + ('已找到，仍需實際輸出測試。' if ready else '尚不完整；可使用 --font 指定其他中文字型。'))
    return 0 if ready else 2


if __name__ == '__main__':
    sys.exit(main())
