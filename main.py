# main.py
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from dotenv import load_dotenv
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv(Path(__file__).resolve().parent / ".env")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден в .env файле")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

async def set_bot_commands(bot: Bot):
    """Установка команд меню бота"""
    commands = [
        BotCommand(command="start", description="🚀 Перезапустить бота"),
        BotCommand(command="make_video", description="🎬 Создать видео"),
        BotCommand(command="upload_images", description="🖼 Загрузить изображения"),
        BotCommand(command="settings_frame_duration", description="🕒 Длительность кадра"),
        BotCommand(command="settings_transition_duration", description="🔁 Длительность перехода"),
        BotCommand(command="settings_transition_type", description="🎞 Тип перехода"),
        BotCommand(command="settings_aspect_ratio", description="📐 Формат видео"),
        BotCommand(command="current_settings", description="⚙️ Текущие настройки")
    ]
    await bot.set_my_commands(commands)

async def main():
    """Основная функция запуска бота"""
    # Импортируем обработчики здесь, чтобы избежать circular imports
    from handlers import menu, video_commands
    from handlers.upload import upload_router
    
    # Подключаем роутеры
    dp.include_router(menu.router)
    dp.include_router(video_commands.router)
    dp.include_router(upload_router)
    
    # Устанавливаем команды бота
    await set_bot_commands(bot)
    
    # Запускаем поллинг
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)