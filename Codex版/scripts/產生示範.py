from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from 環境工具 import find_ffmpeg

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('缺少 Pillow，請先依授權準備 Pillow。')

ROOT = Path(__file__).resolve().parent.parent
W, H = 1280, 720
FPS = 24


def font_path(requested: str | None) -> Path:
    if requested:
        p = Path(requested).expanduser()
        if p.is_file():
            return p
        raise ValueError(f'找不到指定字型：{p}')
    windir = Path(os.environ.get('WINDIR', r'C:\Windows'))
    choices = [windir / 'Fonts' / 'msjh.ttc', windir / 'Fonts' / 'msjhbd.ttc',
               Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
    for p in choices:
        if p.is_file():
            return p
    raise ValueError('找不到中文字型；請使用 --font 指定已存在的中文字型。')


def wrap_lines(draw, text, font, max_width):
    lines, line = [], ''
    for char in text:
        if char == '\n':
            lines.append(line)
            line = ''
        elif draw.textlength(line + char, font=font) > max_width and line:
            lines.append(line)
            line = char
        else:
            line += char
    if line:
        lines.append(line)
    return lines


def render_card(data, scene, index, total, font_file, output, has_voice=False):
    image = Image.new('RGB', (W, H), '#f7f5ee')
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(str(font_file), 64)
    body_font = ImageFont.truetype(str(font_file), 46)
    note_font = ImageFont.truetype(str(font_file), 32)
    draw.rounded_rectangle((50, 46, 1230, 674), radius=26, fill='#ffffff', outline='#d9e7e3', width=3)
    draw.text((95, 88), f"{data['title']}  ·  {index + 1}/{total}", font=note_font, fill='#397f78')
    draw.text((95, 160), scene['heading'], font=title_font, fill='#1b3432')
    y = 270
    for line in wrap_lines(draw, scene['body'], body_font, 1050):
        draw.text((95, y), line, font=body_font, fill='#202e2c')
        y += 68
    if y > 460:
        raise ValueError('內文過長，請縮短文字。')
    draw.rounded_rectangle((95, 475, 1185, 580), radius=16, fill='#e6f3ef')
    lines = wrap_lines(draw, scene['example'], note_font, 1030)
    if len(lines) > 2:
        raise ValueError('例子過長，請縮短文字。')
    for n, line in enumerate(lines):
        draw.text((120, 490 + n * 42), line, font=note_font, fill='#215a52')
    draw.text((95, 620), '課堂示範｜教學卡片', font=note_font, fill='#526c67')
    image.save(output)


def main():
    ap = argparse.ArgumentParser(description='使用 CPU 建立繁體中文靜音教學卡片 MP4。')
    ap.add_argument('--config', default=str(ROOT / '示例' / '內容.json'))
    ap.add_argument('--output', required=True)
    ap.add_argument('--font', default=None)
    ap.add_argument('--audio', default=None, help='可選：已準備好的本機旁白音檔；過短會補靜音，過長截至影片長度')
    ap.add_argument('--tts', action='store_true', help='使用 Edge TTS 線上生成中文旁白，會傳送逐場旁白文字')
    ap.add_argument('--force', action='store_true', help='明確允許覆寫輸出')
    args = ap.parse_args()
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise ValueError('找不到 ffmpeg；請先依授權準備 FFmpeg。')
    config_path = Path(args.config).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if output.suffix.lower() != '.mp4':
        raise ValueError('輸出檔案須為 .mp4。')
    if output == config_path:
        raise ValueError('輸出路徑不能與內容檔相同。')
    if output.exists() and not args.force:
        raise ValueError('輸出檔已存在；請改名，或明確使用 --force。')
    if args.tts and args.audio:
        raise ValueError('--tts 和 --audio 請只選一種。')
    srt_path = output.with_suffix('.srt')
    if args.tts and srt_path.exists() and not args.force:
        raise ValueError('同名字幕檔已存在；請改名，或明確使用 --force。')
    data = json.loads(config_path.read_text(encoding='utf-8-sig'))
    scenes = data.get('scenes', [])
    if not data.get('title') or not 1 <= len(scenes) <= 12:
        raise ValueError('請提供標題及 1–12 個場景。')
    for scene in scenes:
        if not all(isinstance(scene.get(k), str) and scene[k].strip() for k in ('heading', 'body', 'example')):
            raise ValueError('場景需要 heading、body 和 example 文字。')
        if not 1 <= float(scene.get('seconds', 0)) <= 60:
            raise ValueError('場景 seconds 須介於 1–60 秒。')
        if args.tts and (not isinstance(scene.get('narration'), str) or not scene['narration'].strip()):
            raise ValueError('使用 --tts 時每場必須提供 narration 旁白文字。')
    fpath = font_path(args.font)
    audio_path = Path(args.audio).expanduser().resolve() if args.audio else None
    if audio_path and not audio_path.is_file():
        raise ValueError(f'找不到音檔：{audio_path}')
    if audio_path and output == audio_path:
        raise ValueError('輸出路徑不能與輸入音檔相同。')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cpu-demo-', dir=output.parent) as tmp:
        voice_files = []
        if args.tts:
            try:
                import edge_tts
                from mutagen.mp3 import MP3
            except ImportError as exc:
                raise ValueError('使用 --tts 需要安裝 edge-tts 與 mutagen。') from exc
            print('正在將旁白文字送到 Edge TTS 線上服務。')
            for i, scene in enumerate(scenes):
                voice = Path(tmp) / f'voice-{i:02d}.mp3'
                edge_tts.Communicate(scene['narration'], 'zh-TW-HsiaoChenNeural', rate='-5%').save_sync(str(voice))
                if not voice.is_file() or voice.stat().st_size < 1000:
                    raise ValueError('旁白生成失敗，沒有產生有效音檔。')
                scene['seconds'] = max(float(scene['seconds']), MP3(voice).info.length + 0.3)
                voice_files.append(voice)
        images = []
        for i, scene in enumerate(scenes):
            path = Path(tmp) / f'scene-{i:02d}.png'
            render_card(data, scene, i, len(scenes), fpath, path, bool(voice_files))
            images.append(path)
        cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y' if args.force else '-n']
        for path, scene in zip(images, scenes):
            cmd += ['-loop', '1', '-framerate', str(FPS), '-t', str(scene['seconds']), '-i', str(path)]
        if audio_path:
            cmd += ['-i', str(audio_path)]
        for voice in voice_files:
            cmd += ['-i', str(voice)]
        chains = [f'[{i}:v]setsar=1[v{i}]' for i in range(len(images))]
        if voice_files:
            for i, scene in enumerate(scenes):
                chains.append(f'[{len(images)+i}:a]apad=whole_dur={scene["seconds"]},atrim=duration={scene["seconds"]},asetpts=PTS-STARTPTS[a{i}]')
            join = ''.join(f'[v{i}][a{i}]' for i in range(len(images)))
            chains.append(f'{join}concat=n={len(images)}:v=1:a=1[v][a]')
        else:
            join = ''.join(f'[v{i}]' for i in range(len(images)))
            chains.append(f'{join}concat=n={len(images)}:v=1:a=0[v]')
        cmd += ['-filter_complex', ';'.join(chains), '-map', '[v]', '-c:v', 'libx264', '-threads', '2',
                '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
        if audio_path:
            cmd += ['-map', f'{len(images)}:a:0', '-af', 'apad', '-c:a', 'aac',
                    '-t', str(sum(float(scene['seconds']) for scene in scenes))]
        elif voice_files:
            cmd += ['-map', '[a]', '-c:a', 'aac']
        cmd += [str(output)]
        subprocess.run(cmd, check=True)
    print(f'已輸出影片：{output}')
    if args.tts:
        def timecode(seconds):
            ms = round(seconds * 1000)
            return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
        now = 0.0
        entries = []
        for i, scene in enumerate(scenes):
            end = now + float(scene['seconds'])
            entries.append(f'{i+1}\n{timecode(now)} --> {timecode(end)}\n{scene["narration"]}\n')
            now = end
        srt_path.write_text('\n'.join(entries), encoding='utf-8')
        print(f'已輸出分場字幕初稿：{srt_path}；請逐句聽審時間與內容。')
    elif audio_path:
        print('使用已提供的音檔，請實際聽審、核對各畫面與聲音同步。')
    else:
        print('本示範沒有旁白或獨立字幕軌；請實際播放檢查。')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'無法完成：{exc}', file=sys.stderr)
        sys.exit(1)
