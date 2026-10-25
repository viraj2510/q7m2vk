"""Build a narrated MP4 from captured app screens and technical slides.

Requires Pillow, imageio-ffmpeg and Windows System.Speech-generated WAV files.
See docs/video/ for local output; video binaries are deliberately not committed.
"""
import json
import subprocess
import sys
import textwrap
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.video-tools'))
import imageio_ffmpeg

OUT=ROOT/'docs'/'video'
FONT='C:/Windows/Fonts/segoeui.ttf'
BOLD='C:/Windows/Fonts/segoeuib.ttf'
def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)

segments=json.loads((ROOT/'docs'/'narration.json').read_text(encoding='utf-8'))
for i,segment in enumerate(segments):
    canvas=Image.new('RGB',(1920,1080),'#f4f7f6')
    draw=ImageDraw.Draw(canvas)
    draw.rectangle((0,0,1920,12),fill='#008779')
    draw.text((70,42),segment['part'],font=font(22,True),fill='#008779')
    draw.text((70,90),segment['title'],font=font(46,True),fill='#203b38')
    if segment.get('image'):
        screenshot=Image.open(OUT/segment['image']).convert('RGB')
        # Preserve readability: crop the application header/controls/chart area.
        screenshot=screenshot.crop((220,75,screenshot.width-10,min(1040,screenshot.height)))
        screenshot.thumbnail((1330,830),Image.Resampling.LANCZOS)
        canvas.paste(screenshot,(70,180))
        draw=ImageDraw.Draw(canvas)
        label=['National wind\nDay-ahead decisions','As-of selection\nNo later revisions','744 matched hours\nJanuary cohort','Audit trail\nCSV export'][i]
        draw.multiline_text((1510,250),label,font=font(29,True),fill='#236149',spacing=18)
    else:
        for j,bullet in enumerate(segment['bullets']):
            y=230+j*132
            draw.ellipse((80,y+12,94,y+26),fill='#008779')
            draw.text((125,y),bullet,font=font(31),fill='#203b38')
    draw.text((70,1025),'WIND DESK  /  JANUARY 2026 PILOT',font=font(19),fill='#72877b')
    draw.text((1710,1025),f'{i+1} / {len(segments)}',font=font(19),fill='#72877b')
    png=OUT/f'slide-{i}.png'
    canvas.save(png)
    wav=OUT/f'voice-{i}.wav'
    with wave.open(str(wav)) as audio: duration=audio.getnframes()/audio.getframerate()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-loop','1','-i',str(png),'-i',str(wav),'-c:v','libx264','-tune','stillimage','-preset','fast','-r','12','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(duration),str(OUT/f'part-{i}.mp4')],check=True)
    print(f'Segment {i+1}: {duration:.1f}s',flush=True)
(OUT/'concat.txt').write_text('\n'.join(f"file 'part-{i}.mp4'" for i in range(len(segments))))
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-c','copy','-movflags','+faststart',str(OUT/'wind-desk-demo.mp4')],check=True)
print(OUT/'wind-desk-demo.mp4')
