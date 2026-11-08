"""只在本工作包的 .venv 內安裝範例依賴，不變更全域 PATH。"""
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / '.venv'
if sys.version_info < (3, 10):
    sys.exit('需 Python 3.10 以上；請先安裝符合學校規範的 Python。')
python = VENV / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
if not python.exists():
    print('建立工作區虛擬環境：', VENV, flush=True)
    venv.create(VENV, with_pip=True)
print('安裝固定版本依賴（需要網路）：', flush=True)
subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')], check=True)
print('執行課前檢查：', flush=True)
subprocess.run([str(python), '-X', 'utf8', str(ROOT / 'scripts/課前檢查.py')], check=True, cwd=ROOT)
