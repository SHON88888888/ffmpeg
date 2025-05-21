# upload.py

import logging
from aiogram import Router
from aiogram.types import Message
from pathlib import Path

UPLOAD_FOLDER = Path("/opt/animation/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

upload_router = Router()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("upload_handler.log", encoding="utf-8")
logger.addHandler(handler)

@upload_router.message(lambda msg: msg.photo)
async def handle_photo_upload(message: Message):
    try:
        photo = message.photo[-1]  # берём самое большое изображение
        file = await message.bot.get_file(photo.file_id)
        file_path = file.file_path
        filename = f"{photo.file_id}.jpg"
        saved_path = UPLOAD_FOLDER / filename
        await message.bot.download_file(file_path, destination=saved_path)
        await message.answer(f"✅ Фото сохранено: {filename}")
        logger.info(f"Photo saved to {saved_path}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке фото: {e}")
        await message.answer("❌ Не удалось сохранить фото.")

@upload_router.message(lambda msg: msg.document and msg.document.mime_type.startswith("image/"))
async def handle_document_upload(message: Message):
    try:
        file = await message.bot.get_file(message.document.file_id)
        file_path = file.file_path
        filename = message.document.file_name or f"img_{message.document.file_id}.jpg"
        saved_path = UPLOAD_FOLDER / filename
        await message.bot.download_file(file_path, destination=saved_path)
        await message.answer(f"✅ Изображение сохранено: {filename}")
        logger.info(f"Image document saved to {saved_path}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке документа: {e}")
        await message.answer("❌ Не удалось сохранить изображение.")
