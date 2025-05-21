# file: ffmpeg_creator.py | created: 2025-05-03 02:20 (UTC+3)

import subprocess
import tempfile
from pathlib import Path
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_video_with_ffmpeg(
    images: list,
    music_path: str,
    output_path: str,
    frame_duration: float = 2.0,
    resolution: tuple = (1080, 1080),
    transition_type: str = "fade",
    transition_duration: float = 1.0,
    fps: int = 30
):
    temp_dir = Path(tempfile.mkdtemp(prefix="ffmpeg_frames_"))
    try:
        logger.info(f"Создание кадров в {temp_dir}")
        frame_paths = []

        for i, img_path in enumerate(images):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img = img.resize(resolution)
                frame_file = temp_dir / f"frame_{i:04d}.png"
                img.save(frame_file)
                frame_paths.append(str(frame_file))

        input_txt = temp_dir / "input.txt"
        with open(input_txt, "w") as f:
            for path in frame_paths:
                f.write(f"file '{path}'\n")
                f.write(f"duration {frame_duration}\n")
            f.write(f"file '{frame_paths[-1]}'\n")

        temp_video = temp_dir / "video.mp4"
        cmd_video = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(input_txt),
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            "-vf", f"fps={fps}",
            "-s", f"{resolution[0]}x{resolution[1]}",
            str(temp_video)
        ]
        subprocess.run(cmd_video, check=True)

        cmd_audio = [
            "ffmpeg",
            "-y",
            "-i", str(temp_video),
            "-i", str(music_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]
        subprocess.run(cmd_audio, check=True)

        logger.info(f"Видео создано: {output_path}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка FFmpeg: {e}")
        raise RuntimeError(f"FFmpeg error: {e}")
    finally:
        for file in temp_dir.glob("*"):
            file.unlink()
        temp_dir.rmdir()
