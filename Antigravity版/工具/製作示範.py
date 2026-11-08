#!/usr/bin/env python3
"""使用 Pillow/FFmpeg 產生簡短教學示例。預設無旁白；--tts 透過 Edge TTS 傳送文字。"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1280, 720, 24


def run(command, cwd=None, timeout=120):
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"指令失敗：{command[0]}\n{result.stderr[-2000:]}")
    return result.stdout


def stamp(seconds):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def main():
    p = argparse.ArgumentParser(description="CPU 產生示範教學短片")
    p.add_argument("--input", default=str(ROOT / "示範" / "分數相加.json"))
    p.add_argument("--output", default=str(ROOT / "成果" / "示範"), help="新建或空白的輸出資料夾")
    p.add_argument("--font", help="可顯示繁體中文的字型路徑")
    p.add_argument("--tts", action="store_true", help="使用 edge-tts 線上產生中文旁白；會傳送旁白文字")
    p.add_argument("--voice", default="zh-TW-HsiaoChenNeural")
    args = p.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        try:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass
    if not ffmpeg:
        raise RuntimeError("找不到 FFmpeg；先建立工作區環境。")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("目前 Python 未安裝 Pillow。") from exc
    src = Path(args.input).resolve()
    data = json.loads(src.read_text(encoding="utf-8-sig"))
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise RuntimeError("JSON 缺少 scenes。")
    candidates = [Path(args.font)] if args.font else [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / n for n in ("msjhbd.ttc", "msjh.ttc")]
    font_path = next((f for f in candidates if f.is_file()), None)
    if not font_path:
        raise RuntimeError("找不到可用中文字型；請用 --font 指定路徑。")
    target_out = Path(args.output).resolve()
    if target_out.exists() and any(target_out.iterdir()):
        raise RuntimeError(f"輸出資料夾不是空的，請選新資料夾：{target_out}")
    target_out.mkdir(parents=True, exist_ok=True)
    big = ImageFont.truetype(str(font_path), 62)
    body = ImageFont.truetype(str(font_path), 54)
    small = ImageFont.truetype(str(font_path), 26)

    # 由於在 Google Drive 等網路虛擬磁碟上頻繁 seek/write 容易遭檔案系統鎖定超時，
    # 故先於本機暫存目錄完成影音合成，完成後再完整拷貝至輸出資料夾。
    with tempfile.TemporaryDirectory(prefix="video_build_") as tmp_dir:
        out = Path(tmp_dir)
        frame_durations, transcript = [], []
        for index, scene in enumerate(scenes, 1):
            title, detail, narration = (str(scene.get(k, "")).strip() for k in ("title", "detail", "narration"))
            if not title or not detail or not narration:
                raise RuntimeError(f"第 {index} 場須提供 title、detail、narration。")
            title_box = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), title, font=big)
            if title_box[2] - title_box[0] > 1110:
                raise RuntimeError(f"第 {index} 場標題過長，請縮短 title。")
            im = Image.new("RGB", (W, H), "#f5f7fb")
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, 24, H), fill="#1457a5")
            d.text((84, 55), f"{index:02} / {len(scenes):02}", font=small, fill="#275c90")
            d.text((84, 125), title, font=big, fill="#152b43")
            d.rounded_rectangle((84, 242, 1196, 386), radius=24, fill="#ffffff", outline="#cbdae9", width=3)
            bbox = d.textbbox((0, 0), detail, font=body)
            if bbox[2] - bbox[0] > 1030:
                raise RuntimeError(f"第 {index} 場文字過長，請縮短 detail。")
            d.text((118, 278), detail, font=body, fill="#1457a5")
            rows = scene.get("quarters", [])
            if len(rows) > 2 or any(not isinstance(n, int) or n < 0 or n > 4 for n in rows):
                raise RuntimeError("quarters 最多兩列；每列必須為 0 到 4 的整數。")
            for row, filled in enumerate(rows):
                for q in range(4):
                    x = 90 + q * 104
                    y = 435 + row * 78
                    d.rounded_rectangle((x, y, x + 90, y + 62), radius=7,
                                        fill="#2871c0" if q < filled else "#ffffff", outline="#3b6f9d", width=3)
            if rows:
                d.text((84, 658), "以四等分作為示意", font=small, fill="#536b83")
            image_file = f"scene{index:02}.png"
            im.save(out / image_file)
            audio_file = f"voice{index:02}.mp3"
            duration = 5.0
            if args.tts:
                # The spoken text is sent to the Edge TTS service. No audio file is uploaded.
                run([sys.executable, "-m", "edge_tts", "--voice", args.voice, "--text", narration,
                     "--write-media", audio_file], cwd=out, timeout=90)
                try:
                    from mutagen.mp3 import MP3
                except ImportError as exc:
                    raise RuntimeError("有聲示範需要安裝 mutagen。") from exc
                duration = max(duration, MP3(out / audio_file).info.length + 0.35)
            duration = math.ceil(duration * FPS) / FPS
            if args.tts:
                audio_args = ["-i", audio_file]
            else:
                audio_args = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
            segment = f"segment{index:02}.mp4"
            run([ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                 "-i", image_file, *audio_args, "-vf", "format=yuv420p", "-af", "apad",
                 "-t", f"{duration:.6f}", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                 "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", segment], cwd=out)
            frame_durations.append(duration)
            transcript.append(narration)
            print(f"場景 {index}/{len(scenes)}：{duration:.2f} 秒")
        (out / "concat.txt").write_text("".join(f"file 'segment{i:02}.mp4'\n" for i in range(1, len(scenes)+1)), encoding="ascii")
        run([ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
             "-c", "copy", "-movflags", "+faststart", "教學示範.mp4"], cwd=out)
        t = 0.0
        cues = []
        for idx, (text, duration) in enumerate(zip(transcript, frame_durations), 1):
            cues.append(f"{idx}\n{stamp(t)} --> {stamp(t + duration)}\n{text}\n")
            t += duration
        (out / "旁白稿.txt").write_text("\n".join(transcript) + "\n", encoding="utf-8")
        # These are script-based rough cue durations, not word-aligned recognition results.
        (out / "字幕初稿.srt").write_text("\n".join(cues), encoding="utf-8")
        (out / "處理說明.txt").write_text("輸出：" + ("Edge TTS 旁白" if args.tts else "靜音示範") +
            "；字幕按場景估時，未逐字對齊；檢查播放、文字、聲音及畫面後才可交付。\n", encoding="utf-8")
        
        # 拷貝成果至指定輸出目錄
        for item in out.iterdir():
            dest = target_out / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)

    print(f"完成：{target_out / '教學示範.mp4'}")
    print("已附旁白稿與字幕初稿；字幕需與實際聲音對照。" if args.tts else "此為靜音示範；字幕初稿是教學腳本，不是語音辨識結果。")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"執行失敗：{exc}", file=sys.stderr)
        sys.exit(1)
