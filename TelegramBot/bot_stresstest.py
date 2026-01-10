# network_stress_bot.py
import asyncio
import aiohttp
import time
from datetime import datetime
import random
import string
from PIL import Image, ImageDraw
import io
import sys


class NetworkStressTester:
    def __init__(self, bot_token: str, chat_id: int):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    async def test_small_message(self, session):
        """Тест маленьких сообщений"""
        start = time.time()
        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": f"📤 Тест {datetime.now().strftime('%H:%M:%S.%f')[:-3]}"
        }

        try:
            async with session.post(url, json=payload, timeout=5) as resp:
                return time.time() - start, resp.status
        except Exception as e:
            return None, str(e)

    async def test_large_message(self, session, size_kb: int = 100):
        """Тест больших сообщений (до 4096 символов)"""
        start = time.time()
        url = f"{self.api_url}/sendMessage"

        # Генерируем большой текст
        text = ''.join(random.choices(string.ascii_letters + string.digits, k=size_kb * 1024))
        text = text[:4096]  # Максимум для Telegram

        payload = {
            "chat_id": self.chat_id,
            "text": text
        }

        try:
            async with session.post(url, json=payload, timeout=10) as resp:
                return time.time() - start, resp.status
        except Exception as e:
            return None, str(e)

    def generate_test_image(self, width: int, height: int):
        """Генерация тестового изображения"""
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # Рисуем что-то
        for i in range(100):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)

        # Сохраняем в байты
        img_byte_arr = io.BytesIO()
        quality = 95 if width * height > 1000000 else 85
        img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
        img_byte_arr.seek(0)

        return img_byte_arr, len(img_byte_arr.getvalue())

    async def test_photo_upload(self, session, width: int, height: int):
        """Тест загрузки фото"""
        start = time.time()
        url = f"{self.api_url}/sendPhoto"

        # Генерируем изображение
        image_bytes, size_bytes = self.generate_test_image(width, height)
        size_kb = size_bytes / 1024

        form_data = aiohttp.FormData()
        form_data.add_field('chat_id', str(self.chat_id))
        form_data.add_field('photo', image_bytes, filename=f'test_{width}x{height}.jpg')
        form_data.add_field('caption', f'Тест: {width}x{height} ({size_kb:.1f} КБ)')

        try:
            async with session.post(url, data=form_data, timeout=30) as resp:
                return time.time() - start, resp.status, size_kb
        except Exception as e:
            return None, str(e), size_kb

    async def stress_test(self, duration_seconds: int = 60):
        """Стресс-тест на указанное время"""
        print(f"🚀 Запуск стресс-теста на {duration_seconds} секунд...")
        print(f"📅 Время начала: {datetime.now()}")
        print("=" * 60)

        # Создаем connector внутри event loop
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)

        async with aiohttp.ClientSession(connector=connector) as session:
            end_time = time.time() + duration_seconds
            test_count = 0
            success_count = 0
            total_data_sent = 0

            while time.time() < end_time:
                test_count += 1

                # Выбираем случайный тест
                test_type = random.choice(['small', 'large', 'photo_small', 'photo_large'])

                try:
                    if test_type == 'small':
                        delay, status = await self.test_small_message(session)
                        if delay and status == 200:
                            success_count += 1
                            print(f"✅ Тест {test_count}: Маленькое сообщение - {delay * 1000:.0f} мс")
                        else:
                            print(f"❌ Тест {test_count}: Ошибка - {status}")

                    elif test_type == 'large':
                        delay, status = await self.test_large_message(session, 50)
                        if delay and status == 200:
                            success_count += 1
                            total_data_sent += 50  # ~50 КБ
                            print(f"✅ Тест {test_count}: Большое сообщение - {delay * 1000:.0f} мс")
                        else:
                            print(f"❌ Тест {test_count}: Ошибка - {status}")

                    elif test_type == 'photo_small':
                        delay, status, size = await self.test_photo_upload(session, 800, 600)
                        if delay and status == 200:
                            success_count += 1
                            total_data_sent += size
                            print(f"✅ Тест {test_count}: Фото 800x600 - {delay * 1000:.0f} мс ({size:.1f} КБ)")
                        else:
                            print(f"❌ Тест {test_count}: Ошибка - {status}")

                    elif test_type == 'photo_large':
                        delay, status, size = await self.test_photo_upload(session, 1920, 1080)
                        if delay and status == 200:
                            success_count += 1
                            total_data_sent += size
                            print(f"✅ Тест {test_count}: Фото 1920x1080 - {delay * 1000:.0f} мс ({size:.1f} КБ)")
                        else:
                            print(f"❌ Тест {test_count}: Ошибка - {status}")

                    # Небольшая пауза между тестами
                    await asyncio.sleep(random.uniform(0.1, 0.5))

                except Exception as e:
                    print(f"⚠️  Тест {test_count}: Исключение - {type(e).__name__}: {e}")

            # Итоги
            print("\n" + "=" * 60)
            print("📊 РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТА:")
            print(f"   Всего тестов: {test_count}")
            print(f"   Успешных: {success_count} ({success_count / test_count * 100:.1f}%)")
            print(f"   Отправлено данных: {total_data_sent / 1024:.2f} МБ")
            print(f"   Время: {duration_seconds} секунд")
            print(f"   Скорость: {total_data_sent / duration_seconds:.1f} КБ/сек")
            print(f"📅 Время окончания: {datetime.now()}")

            if success_count / test_count < 0.8:
                print("⚠️  ВНИМАНИЕ: Много ошибок. Возможны проблемы с сетью!")
            else:
                print("✅ Тест пройден успешно!")


async def main():
    # Настройки
    BOT_TOKEN = "8034081320:AAHWQZRf5LNS8bzdyDLXpiMYQvFdKGKWmUU"
    CHAT_ID = 413700636  # твой ID

    # Получаем длительность теста из аргументов или используем по умолчанию
    if len(sys.argv) > 1:
        try:
            TEST_DURATION = int(sys.argv[1])
        except:
            TEST_DURATION = 30
    else:
        TEST_DURATION = 30  # секунд для теста

    tester = NetworkStressTester(BOT_TOKEN, CHAT_ID)

    print("⚡ TELEGRAM NETWORK STRESS TEST ⚡")
    print(f"Бот: {BOT_TOKEN[:10]}...")
    print(f"Чат: {CHAT_ID}")
    print(f"Длительность: {TEST_DURATION} секунд")
    print("-" * 40)

    try:
        await tester.stress_test(TEST_DURATION)
    except KeyboardInterrupt:
        print("\n⏹️  Тест прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершено")