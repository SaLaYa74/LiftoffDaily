"""Reel engine: a real photo with a slow cinematic push-in (moving from frame 1), text beats that pop in
over it, an original ambient bed. Frames are composited in Pillow and piped straight into ffmpeg."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from PIL import Image, ImageEnhance

from . import look as K
from .music import make_ambient
from .render import html_to_png

FPS = 30
W, H = 1080, 1920
HANDLE = "@liftoff_daily"


@dataclass
class Beat:
    html: str          # overlay page (from look.py)
    seconds: float


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
    except ImportError:
        exe = shutil.which("ffmpeg")
        if exe:
            return exe
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "imageio-ffmpeg"], check=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _ease(x):
    return x * x * (3 - 2 * x)          # smoothstep: no jolt at the start or end of the move


def _prepare(photo, max_zoom, grade=None):
    """Scale the photo once so the widest 9:16 crop is ~1.6x the output: sharp at every zoom, fast to resample.
    grade=(brightness, contrast, color) lifts dim night shots; never used to add or remove anything."""
    im = Image.open(photo).convert("RGB")
    iw, ih = im.size
    cw, ch = (iw, iw * 16 / 9) if iw / ih < 9 / 16 else (ih * 9 / 16, ih)   # largest 9:16 window
    scale = min(1.0, (W * 1.6 * max_zoom) / cw)
    if scale < 1.0:
        im = im.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
        cw, ch = cw * scale, ch * scale
    if grade:
        for enhance, amount in zip((ImageEnhance.Brightness, ImageEnhance.Contrast, ImageEnhance.Color), grade):
            im = enhance(im).enhance(amount)
    return im, cw, ch


def _box(im, cw, ch, zoom, cx, cy):
    """9:16 crop box at `zoom` centered near (cx, cy) in 0-1 image coords, clamped inside the photo."""
    w, h = cw / zoom, ch / zoom
    x = min(max(cx * im.width - w / 2, 0), im.width - w)
    y = min(max(cy * im.height - h / 2, 0), im.height - h)
    return (x, y, x + w, y + h)


def photo_reel(out_dir, name, photo, credit, beats, seed, focus=((0.5, 0.5), (0.5, 0.5)), zoom=(1.0, 1.22),
               layout="high", grade=None):
    """beats: [Beat, ...] shown back to back; the first is fully visible on frame 1. Returns (mp4, cover_jpg)."""
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="bse_reel_")
    try:
        pages = [K.frame_layer(HANDLE, credit, layout)] + [b.html for b in beats]
        pngs = [os.path.join(work, f"layer{i}.png") for i in range(len(pages))]
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(lambda pp: html_to_png(pp[0], pp[1], "reel"), zip(pages, pngs)))
        frame, *layers = [Image.open(p).convert("RGBA") for p in pngs]

        im, cw, ch = _prepare(photo, max(zoom), grade)
        total = sum(b.seconds for b in beats)
        n = round(total * FPS)
        starts, t = [], 0.0
        for b in beats:
            starts.append(t)
            t += b.seconds

        audio = os.path.join(work, "bed.wav")
        make_ambient(audio, total + 0.1, seed)
        mp4 = os.path.join(out_dir, f"{name}.mp4")
        ff = subprocess.Popen([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
                               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-maxrate", "7M", "-bufsize", "14M", "-profile:v", "high",
                               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                               "-shortest", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
        cover = None
        (fx0, fy0), (fx1, fy1) = focus
        for i in range(n):
            t = i / FPS
            p = _ease(i / max(1, n - 1))
            z = zoom[0] + (zoom[1] - zoom[0]) * p
            box = _box(im, cw, ch, z, fx0 + (fx1 - fx0) * p, fy0 + (fy1 - fy0) * p)
            out = im.resize((W, H), Image.BICUBIC, box=box).convert("RGBA")
            out.alpha_composite(frame)
            k = max(j for j, s in enumerate(starts) if s <= t + 1e-6)
            age = t - starts[k]
            left = starts[k] + beats[k].seconds - t
            layer = layers[k]
            if k == 0:
                # the hook is readable on frame 1; it settles from 104% so something moves immediately
                s = 1.04 - 0.04 * _ease(min(1, age / 0.5))
                alpha = 1.0
            else:
                s = 0.94 + 0.06 * _ease(min(1, age / 0.22))
                alpha = min(1.0, age / 0.16)
            if k < len(beats) - 1 and left < 0.12:
                alpha *= max(0.0, left / 0.12)
            if abs(s - 1) > 1e-3:
                lw, lh = round(W * s), round(H * s)
                big = layer.resize((lw, lh), Image.BICUBIC)
                layer = Image.new("RGBA", (W, H))
                layer.paste(big, ((W - lw) // 2, (H - lh) // 2))     # centered; clips when larger
            if alpha < 1:
                a = layer.getchannel("A").point(lambda v: int(v * alpha))
                layer = layer.copy()
                layer.putalpha(a)
            out.alpha_composite(layer)
            rgb = out.convert("RGB")
            if i == min(n - 1, round(0.6 * FPS)):
                cover = rgb.copy()                     # the hook, settled: works as the grid tile
            ff.stdin.write(rgb.tobytes())
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg failed while encoding the Reel")
        cover_path = os.path.join(out_dir, f"{name}_cover.jpg")
        cover.save(cover_path, "JPEG", quality=95, subsampling=0)
        return mp4, cover_path
    finally:
        shutil.rmtree(work, ignore_errors=True)


def video_checks(rep, mp4):
    """Instagram Reels requirements + sanity: 9:16 1080x1920, 3-90s, has audio, < 20MB (CDN limit)."""
    name = os.path.basename(mp4)
    if not rep.require(os.path.exists(mp4), f"{name}: rendered", "video missing"):
        return
    size_mb = os.path.getsize(mp4) / 1e6
    rep.require(0.2 < size_mb < 20, f"{name}: file size", f"{size_mb:.1f} MB")
    info = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", mp4], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    secs = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3)) if dur else 0
    rep.require(3 <= secs <= 90, f"{name}: duration", f"{secs:.1f}s (needs 3-90s)")
    rep.require("1080x1920" in info, f"{name}: 1080x1920", "wrong resolution")
    rep.require("Audio: aac" in info, f"{name}: has audio", "no AAC audio track")
    rep.require("Video: h264" in info, f"{name}: H.264 video", "wrong codec")
