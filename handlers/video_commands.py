# video_commands.py
import asyncio
import json
import logging
from pathlib import Path
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from ffmpeg_creator import create_video_with_ffmpeg

router = Router()
logger = logging.getLogger(__name__)

# Пути к файлам и папкам
IMAGES_FOLDER = Path("/opt/animation/images")
MUSIC_FOLDER = Path("/opt/animation/music")
OUTPUT_VIDEO = Path("/opt/animation/output/output.mp4")
SETTINGS_FILE = Path("/opt/animation/video_settings.json")

# Создаем папки, если их нет
IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
MUSIC_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

@router.message(Command("make_video"))
async def cmd_make_video(message: types.Message):
    """Обработчик команды создания видео"""
    try:
        # Получаем список изображений
        images = sorted(
            p for p in IMAGES_FOLDER.iterdir() 
            if p.suffix.lower() in (".jpg", ".jpeg", ".png")
        )
        
        if not images:
            await message.answer("❌ Нет изображений для создания видео! Загрузите их через /upload_images")
            return

        # Проверяем наличие музыки
        music_files = list(MUSIC_FOLDER.glob("*.mp3"))
        music_file = music_files[0] if music_files else None

        # Загружаем настройки
        settings = {
            "frame_duration": 3.0,
            "transition_duration": 1.0,
            "transition_type": "fade",
            "aspect_ratio": "square"
        }
        
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                settings.update(json.load(f))

        # Отправляем сообщение о начале обработки
        progress_msg = await message.answer(
            "🔄 Начинаю создание видео...\n"
            f"📊 Параметры:\n"
            f"- Кадров: {len(images)}\n"
            f"- Длительность кадра: {settings['frame_duration']} сек\n"
            f"- Переход: {settings['transition_type']} ({settings['transition_duration']} сек)\n"
            f"- Формат: {settings['aspect_ratio']}\n"
            f"⏳ Ожидаемое время: ~{len(images) * (settings['frame_duration'] + settings['transition_duration'])} сек"
        )

        # Создаем видео
        try:
            await create_video_with_ffmpeg(
                images=images,
                music_path=music_file,
                output_path=OUTPUT_VIDEO,
                frame_duration=settings["frame_duration"],
                transition_type=settings["transition_type"],
                transition_duration=settings["transition_duration"],
                aspect_ratio=settings["aspect_ratio"]
            )
            
            # Отправляем результат
            await message.answer("✅ Видео успешно создано!")
            await message.answer_video(FSInputFile(OUTPUT_VIDEO))
            
        except Exception as e:
            logger.error(f"Ошибка создания видео: {e}", exc_info=True)
            await message.answer(f"❌ Ошибка при создании видео: {str(e)}")
            
        finally:
            # Удаляем сообщение о прогрессе
            await progress_msg.delete()
            
    except Exception as e:
        logger.error(f"Ошибка в cmd_make_video: {e}", exc_info=True)
        await message.answer("❌ Произошла непредвиденная ошибка")