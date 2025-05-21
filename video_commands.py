# file: handlers/video_commands.py | created: 2025-05-03 04:20 (UTC+3)

import logging
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from pathlib import Path
from ffmpeg_creator import create_video_with_ffmpeg

router = Router()

# Настройка директорий
BASE_DIR = Path("/opt/ffmpeg_bot")
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
MUSIC_FILE = BASE_DIR / "assets" / "default.mp3"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

@router.message(Command("make_video"))
async def make_video_handler(message: Message):
    user_id = message.from_user.id
    user_dir = UPLOAD_DIR / str(user_id)
    output_path = OUTPUT_DIR / f"{user_id}_video.mp4"

    if not user_dir.exists() or not any(user_dir.iterdir()):
        await message.answer("⚠️ У вас нет загруженных изображений.")
        return

    images = sorted(user_dir.glob("*.jpg")) + sorted(user_dir.glob("*.png"))
    if not images:
        await message.answer("⚠️ Не найдено изображений (только .jpg и .png).")
        return

    try:
        await message.answer("🎬 Обработка видео, подождите...")
        create_video_with_ffmpeg(
            images=images,
            music_path=MUSIC_FILE,
            output_path=output_path
        )
        await message.answer_video(video=FSInputFile(output_path))
        
        logger.info(f"Видео отправлено пользователю {user_id}")
    except Exception as e:
        logger.exception("❌ Ошибка при создании видео")
        await message.answer("❌ Ошибка при создании видео. Проверь лог.")
