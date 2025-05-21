# menu.py

import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('menu_handler.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

router = Router()

class VideoSettingsStates(StatesGroup):
    waiting_for_frame_duration = State()
    waiting_for_transition_duration = State()
    waiting_for_transition_type = State()
    waiting_for_aspect_ratio = State()

SETTINGS_FILE = Path("/opt/animation/video_settings.json")

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я помогу тебе сделать видео из изображений.\n\n"
        "📥 Чтобы загрузить изображения — используй /upload_images\n"
        "🎬 Чтобы создать ролик — жми /make_video\n"
        "⚙️ А если хочешь — настрой формат и переходы через меню."
    )

@router.message(Command("upload_images"))
async def cmd_upload_images(message: Message):
    await message.answer("📥 Пожалуйста, отправьте одно или несколько изображений (файлом или как фото). Они будут сохранены для видео.")

@router.message(Command("settings_frame_duration"))
async def cmd_frame_duration(message: Message, state: FSMContext):
    await message.answer("🕒 Введите длительность кадра в секундах (например, 3.5):")
    await state.set_state(VideoSettingsStates.waiting_for_frame_duration)

@router.message(VideoSettingsStates.waiting_for_frame_duration)
async def process_frame_duration(message: Message, state: FSMContext):
    try:
        duration = float(message.text.strip())
        if duration <= 0:
            raise ValueError("Duration must be positive")
    except ValueError:
        await message.answer("⚠️ Введите положительное число.")
        return

    settings = {}
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["frame_duration"] = duration

    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    await message.answer(f"✅ Длительность кадра установлена на {duration} секунд.")
    await state.clear()

@router.message(Command("settings_transition_duration"))
async def cmd_transition_duration(message: Message, state: FSMContext):
    await message.answer("🔁 Введите длительность перехода в секундах (например, 1.5):")
    await state.set_state(VideoSettingsStates.waiting_for_transition_duration)

@router.message(VideoSettingsStates.waiting_for_transition_duration)
async def process_transition_duration(message: Message, state: FSMContext):
    try:
        duration = float(message.text.strip())
        if duration <= 0:
            raise ValueError("Duration must be positive")
    except ValueError:
        await message.answer("⚠️ Введите положительное число.")
        return

    settings = {}
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["transition_duration"] = duration

    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    await message.answer(f"✅ Длительность перехода установлена на {duration} секунд.")
    await state.clear()

@router.message(Command("settings_transition_type"))
async def cmd_transition_type(message: Message, state: FSMContext):
    text = (
        "🎞 Выберите тип перехода (введите номер):\n"
        "1. fade (плавное исчезновение)\n"
        "2. slide (сдвиг)\n"
        "3. zoom (приближение)"
    )
    await message.answer(text)
    await state.set_state(VideoSettingsStates.waiting_for_transition_type)

@router.message(VideoSettingsStates.waiting_for_transition_type)
async def process_transition_type(message: Message, state: FSMContext):
    options = {"1": "fade", "2": "slide", "3": "zoom"}
    choice = message.text.strip()
    if choice not in options:
        await message.answer("⚠️ Введите номер из списка: 1, 2 или 3")
        return

    settings = {}
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["transition_type"] = options[choice]

    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    await message.answer(f"✅ Тип перехода установлен: {options[choice]}")
    await state.clear()

@router.message(Command("settings_aspect_ratio"))
async def cmd_aspect_ratio(message: Message, state: FSMContext):
    text = (
        "📐 Выберите формат видео (введите номер):\n"
        "1. Квадратный (1:1)\n"
        "2. Горизонтальный (16:9)\n"
        "3. Вертикальный (9:16)"
    )
    await message.answer(text)
    await state.set_state(VideoSettingsStates.waiting_for_aspect_ratio)

@router.message(VideoSettingsStates.waiting_for_aspect_ratio)
async def process_aspect_ratio(message: Message, state: FSMContext):
    options = {"1": "square", "2": "horizontal", "3": "vertical"}
    choice = message.text.strip()
    if choice not in options:
        await message.answer("⚠️ Введите номер из списка: 1, 2 или 3")
        return

@router.message(Command("current_settings"))
async def cmd_current_settings(message: Message):
    settings = {
        "frame_duration": 8.0,
        "transition_duration": 1.0,
        "transition_type": "fade",
        "aspect_ratio": "square"
    }
    
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            settings.update(json.load(f))
    
    text = (
        "⚙️ Текущие настройки:\n"
        f"🕒 Длительность кадра: {settings['frame_duration']} сек\n"
        f"🔁 Длительность перехода: {settings['transition_duration']} сек\n"
        f"🎞 Тип перехода: {settings['transition_type']}\n"
        f"📐 Формат: {settings['aspect_ratio']}"
    )
    await message.answer(text)

    settings = {}
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["aspect_ratio"] = options[choice]

    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    await message.answer(f"✅ Формат видео установлен: {options[choice]}")
    await state.clear()
