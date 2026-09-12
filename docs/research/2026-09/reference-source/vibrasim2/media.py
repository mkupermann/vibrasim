"""Timestamp-aligned finite media bundles; fixed nonsemantic transduction."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
import wave
import numpy as np

FPS, SAMPLE_RATE = 10, 16000


@dataclass
class Clip:
    title: str
    frames: np.ndarray
    audio: np.ndarray
    label: str | None = None
    supplied_text: str = ""
    source: str = "synthetic"

    def __post_init__(self):
        self.frames = np.asarray(self.frames, dtype=np.float32)
        self.audio = np.asarray(self.audio, dtype=np.float32)
        if self.frames.ndim != 3 or self.frames.shape[1:] != (32, 32) or not len(self.frames):
            raise ValueError("clip requires one or more 32×32 frames")
        if self.audio.ndim != 1 or len(self.audio) != len(self.frames) * (SAMPLE_RATE // FPS):
            raise ValueError("audio/video durations must match")
        if not np.isfinite(self.frames).all() or not np.isfinite(self.audio).all():
            raise ValueError("clip contains nonfinite data")

    @property
    def duration(self):
        return len(self.frames) / FPS

    @property
    def digest(self):
        h = hashlib.sha256(self.frames.tobytes() + self.audio.tobytes())
        h.update(self.supplied_text.encode())
        return h.hexdigest()

    def sample(self, index):
        n = SAMPLE_RATE // FPS
        return self.frames[index], self.audio[index*n:(index+1)*n], self.supplied_text

    def wav(self, path):
        with wave.open(str(path), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SAMPLE_RATE)
            f.writeframes((np.clip(self.audio, -1, 1) * 32767).astype('<i2').tobytes())


def synthetic_clips(seed: int, repeats: int) -> list[Clip]:
    rng = np.random.default_rng(seed)
    clips = []
    y, x = np.mgrid[:32, :32]
    for _ in range(repeats):
        for label, frequency in zip(('ring', 'square', 'cross'), (400, 1000, 2500)):
            dx, dy = rng.uniform(-2, 2, 2)
            frames = []
            for t in range(FPS):
                xx, yy = x-15.5-dx-.6*np.sin(t/3), y-15.5-dy
                radius = np.sqrt(xx*xx+yy*yy)
                if label == 'ring': mask = (radius > 7) & (radius < 11)
                elif label == 'square': mask = (abs(xx)<9) & (abs(yy)<9)
                else: mask = ((abs(xx)<3)&(abs(yy)<12)) | ((abs(yy)<3)&(abs(xx)<12))
                frames.append(np.clip(mask.astype(float)*rng.uniform(.7, 1) + rng.normal(0, .015, (32,32)), 0, 1))
            times = np.arange(SAMPLE_RATE)/SAMPLE_RATE
            audio = rng.uniform(.3, .7)*np.sin(2*np.pi*frequency*times+rng.uniform(0, 2*np.pi))
            audio += rng.normal(0, .005, len(times))
            clips.append(Clip(f'{label} · {frequency} Hz', frames, audio, label))
    rng.shuffle(clips)
    return clips


def import_video(path: Path, *, start: float = 0, duration: float = 20, supplied_text: str = '') -> Clip:
    if not path.is_file() or not np.isfinite(start) or start < 0 or not np.isfinite(duration) or not 0 < duration <= 300:
        raise ValueError('Select an existing video; duration must be 0–300 seconds and start nonnegative.')
    common = ['ffmpeg','-v','error','-ss',str(start),'-i',str(path.resolve()),'-t',str(duration)]
    video = subprocess.run(common+['-vf',f'fps={FPS},scale=32:32','-pix_fmt','gray','-f','rawvideo','pipe:1'], capture_output=True, check=True, timeout=90).stdout
    count = len(video)//1024
    if not count: raise ValueError('Selected segment has no video frames.')
    probe = subprocess.run(['ffprobe','-v','error','-select_streams','a','-show_entries','stream=index','-of','json',str(path.resolve())],capture_output=True,text=True,check=True,timeout=10)
    if json.loads(probe.stdout).get('streams'):
        # Raw PCM discards timestamps. Materialize missing leading samples BEFORE
        # stripping them, otherwise a delayed audio stream moves to video time zero.
        raw = subprocess.run(common+['-vn','-ac','1','-af',f'aresample={SAMPLE_RATE}:async=1:first_pts=0',
                                     '-ar',str(SAMPLE_RATE),'-f','f32le','pipe:1'],capture_output=True,check=True,timeout=90).stdout
        audio = np.frombuffer(raw, '<f4')
    else: audio = np.zeros(0, dtype=np.float32)
    n = count*SAMPLE_RATE//FPS
    audio = np.pad(audio[:n], (0,max(0,n-len(audio))))
    return Clip(path.name,np.frombuffer(video[:count*1024],np.uint8).reshape(count,32,32)/255, audio,
                supplied_text=supplied_text,source=str(path.resolve()))


def import_youtube(url: str, *, duration: float = 20, start: float = 0, supplied_text: str = '') -> Clip:
    u = urlparse(url)
    if u.scheme != 'https' or u.hostname not in {'youtube.com','www.youtube.com','m.youtube.com','youtu.be'}:
        raise ValueError('Use an HTTPS YouTube video URL.')
    if not np.isfinite(duration) or not 0 < duration <= 300 or not np.isfinite(start) or start < 0:
        raise ValueError('Invalid clip interval.')
    with tempfile.TemporaryDirectory(prefix='vibrasim-video-') as d:
        # One selected clip only, no playlists, cookies or account access.
        cmd = [sys.executable,'-m','yt_dlp','--no-playlist','--no-progress',
               '--download-sections',f'*{start}-{start+duration}', '--force-keyframes-at-cuts',
               '--max-filesize','300M','-f','bv*[height<=360]+ba/b[height<=360]',
               '--merge-output-format','mp4','-o',str(Path(d)/'selected.%(ext)s'),'--',url]
        # A project-local runtime avoids altering global shell configuration.
        deno = Path(sys.executable).with_name('deno')
        if deno.is_file():
            cmd[3:3] = ['--js-runtimes', 'deno:' + str(deno)]
        subprocess.run(cmd,capture_output=True,check=True,timeout=180)
        files = [p for p in Path(d).iterdir() if p.suffix in {'.mp4','.webm','.mkv'}]
        if len(files) != 1: raise ValueError('Downloader did not produce one playable video.')
        clip = import_video(files[0],duration=duration,supplied_text=supplied_text)
        clip.source=url; clip.title='Selected YouTube clip'
        return clip
