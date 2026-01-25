import cv2
from datetime import date
import asyncio
import numpy as np
import av
import os




def get_img_sync(debug: bool = False):
    """Синхронная версия для RTSP камеры"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        #result = loop.run_until_complete(get_img(debug))
        result = loop.run_until_complete(get_img_PyAV())
        loop.close()
        return result
    except Exception as e:
        print(f"❌ Ошибка получения фото: {e}")
        return None


async def get_img2(debug: bool = False):
    """Получение изображения с RTSP камеры"""
    print("📡 Подключаюсь к IP-камере по RTSP...")

    # URL вашей камеры (уберите лишний @ если нет пароля)
    #url = "rtsp://admin:@192.168.0.25:554/h264?tcp"
    url = "rtsp://admin:@192.168.0.23:554/h264?tcp&buffer_size=102400"
    alt_urls = [
        "rtsp://admin:@192.168.0.23:554/stream1",  # Основной поток
        "rtsp://admin:@192.168.0.23:554/stream2",  # Субпоток (низкое разрешение)
    ]

    cap = None
    last_frame = None

    for attempt, test_url in enumerate([url] + alt_urls):
        try:
            if debug:
                print(f"  Попытка {attempt + 1}: {test_url}")

            # ⭐ ВАЖНО: Для RTSP нужно использовать параметры
            cap = cv2.VideoCapture(test_url, cv2.CAP_FFMPEG)

            # ⭐ НАСТРОЙКИ ДЛЯ RTSP (важные!)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Минимальный буфер
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            cap.set(cv2.CAP_PROP_FPS, 15)  # Ограничиваем FPS

            # Даем камере время на подключение
            await asyncio.sleep(2)

            if not cap.isOpened():
                print(f"  ❌ Не удалось открыть {test_url}")
                continue

            print(f"  ✅ Подключено к {test_url}")

            # Читаем несколько кадров для прогрева потока
            warmup_frames = []
            for i in range(5):
                ret, frame = cap.read()
                if ret:
                    warmup_frames.append(frame)
                await asyncio.sleep(0.1)

            if not warmup_frames:
                print("  ⚠️ Нет кадров в потоке")
                continue

            # Берем последний кадр
            last_frame = warmup_frames[-1]

            # Проверяем качество кадра
            if is_valid_frame(last_frame):
                print(f"  ✅ Получен валидный кадр {last_frame.shape}")
                break
            else:
                print("  ⚠️ Кадр поврежден, пробую другой URL...")

        except Exception as e:
            print(f"  ❌ Ошибка: {str(e)[:100]}...")
            continue

        finally:
            # Всегда освобождаем ресурсы
            if cap is not None:
                cap.release()
                cap = None

    if last_frame is not None:
        # Улучшаем изображение если нужно
        enhanced = enhance_frame(last_frame, debug)
        return enhanced

    print("❌ Не удалось подключиться к камере")
    return None


def is_valid_frame(frame):
    """Проверяет, что кадр валиден"""
    if frame is None:
        return False

    height, width = frame.shape[:2]

    # Минимальные размеры
    if height < 100 or width < 100:
        return False

    # Проверяем на серый экран (все пиксели одинаковые)
    if np.std(frame) < 5:
        return False

    # Проверяем на цветные полосы
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Проверяем вертикальные градиенты
    col_grad = np.mean(np.abs(np.diff(gray, axis=1)))

    # Проверяем горизонтальные градиенты
    row_grad = np.mean(np.abs(np.diff(gray, axis=0)))

    # Если оба градиента почти нулевые - вероятно полосы/мусор
    if col_grad < 1.0 and row_grad < 1.0:
        return False

    return True


def enhance_frame(frame, debug=False):
    """Улучшает изображение с IP-камеры"""
    if frame is None:
        return None

    height, width = frame.shape[:2]

    # 1. Автоматическая яркость/контраст
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Вычисляем текущую яркость
    mean_brightness = np.mean(gray)

    if debug:
        print(f"  📊 Средняя яркость: {mean_brightness:.1f}")

    # Корректируем если нужно
    if mean_brightness < 50:  # Слишком темно
        alpha = 2.0  # Контраст
        beta = 30  # Яркость
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    elif mean_brightness > 200:  # Слишком ярко
        alpha = 0.8  # Уменьшаем контраст
        beta = -20  # Уменьшаем яркость
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    else:
        enhanced = frame.copy()

    # 2. Уменьшение шума (особенно для ночной съемки)
    enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)

    # 3. Легкое увеличение резкости
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)

    return enhanced


async def get_img_PyAV():
    try:
        camera_path = "rtsp://admin:@192.168.0.23:554/h264?tcp"
        # Опции для стабильности
        options = {
        # Пропуск кадров
        'skip_frame': 'default',           # Пропускать неключевые кадры
        # 'skip_frame': 'nokey',           # Пропускать все кроме ключевых
        # 'skip_frame': 'bidir',           # Пропускать B-кадры
        # 'skip_frame': 'nointra',         # Не пропускать I-кадры

        # Потоки
        'threads': '1',                    # Кол-во потоков декодера
        'refcounted_frames': '1',          # Счетчик ссылок на кадры

        # Оптимизации
        'lowres': '0',                     # 0=полное разрешение, 1=1/2, 2=1/4
        # 'err_detect': 'crccheck',        # Проверка ошибок
    }
        print("📡 Попытка подключения к IP-камере...")
        container = av.open(camera_path, options=options)
    except Exception as e:
        print(f"❌ Не удалось подключиться к камере, Ошибка: {e}")
        return 0
    print("Успешная попытка.")
    result = None
    for index, frame in enumerate(container.decode(video=0)):
        result = frame
        break

    print("📸 Делаю фото...")

    if result is not None:
        if isinstance(result, list) and len(result) > 1:
            print(result[0])
            img = result[1]
        else:
            img = result
            print("✅ Фото получено")

        PHOTO_DIR = "../img/camphoto/"
        FILENAME = "camera_photo_"
        filecount = 0
        for file in os.listdir(PHOTO_DIR):
            if f"{FILENAME}{date.today()}" in file:
                filecount += 1
        if filecount == 0:
            result_image_name = f"{PHOTO_DIR + FILENAME}{date.today()}.jpg"
        else:
            result_image_name = f"{PHOTO_DIR + FILENAME}{date.today()}_{filecount}.jpg"

        result.to_image().save(result_image_name)
        print(f"кадр сохранен, {result_image_name} ")
        return result_image_name

async def camera_test(ip:str = "192.168.0.23:554"):
    try:
        camera_path = f"rtsp://admin:@{ip}/h264?tcp"
        # Опции для стабильности
        print("📡 Попытка подключения к IP-камере...")
        av.open(camera_path)
        return True
    except Exception as e:
        print(f"❌ Не удалось подключиться к камере, Ошибка: {e}")
        return False


if __name__ == '__main__':
    asyncio.run(get_img_PyAV())
    #asyncio.run(get_img2())