import cv2
from datetime import date
import asyncio
import av
import os
from PySide6.QtCore import *
from PySide6.QtGui import QImage
PHOTO_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img", "camphoto"))+"/"
FILE_NAME = "camera_photo_"
FILE_EXTENSION = "jpg"

class CameraThread(QThread):
    change_pixmap_signal = Signal(QImage)

    def __init__(self, url, target_size):
        super().__init__()
        self.url = url
        self.target_size = target_size  # кортеж (width, height)
        self._run_flag = True

    def run(self):
        import concurrent.futures
        from urllib.parse import urlparse
        import socket
        container = None
        options = {
            'rtsp_transport': 'udp',
            'fflags': 'nobuffer',
            'flags': 'low_delay',
            'probesize': '32',
            'analyzeduration': '0',
            'max_delay': '0'
        }
        print("старт подключения.")
        while self._run_flag:

            try:
                # -------- ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ПОРТА ----------
                try:
                    parsed = urlparse(self.url)
                    host = parsed.hostname
                    port = parsed.port
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)  # ждём ответа 2 секунды
                except Exception as e:
                    print(f"ошибка парса строки {e}")
                try:
                    sock.connect((host, port))
                    sock.close()
                except:
                    print("ошибка введенный данных")
                    break
                # ------------------------------------------------


                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: av.open(self.url, options=options))
                    container = future.result(timeout=5)  # ждём открытия до 5 секунд

                stream = container.streams.video[0]
                stream.thread_type = 'AUTO'

                for packet in container.demux(stream):
                    for frame in packet.decode():
                        if not self._run_flag:
                            print("камера не найдена.")
                            break
                        img = frame.to_ndarray(format='rgb24')
                        if (img.shape[1], img.shape[0]) != self.target_size:
                            img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_LINEAR)
                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        self.change_pixmap_signal.emit(qt_image)
                    if not self._run_flag:
                        print("камера не найдена.")
                        break
            except TimeoutError:
                print("время вышло")
                break
            except av.error.InvalidDataError:
                print("неверно указаны данные")
                break
            except av.error.HTTPUnauthorizedError:
                print("неверно указан логин или пароль")
                break
            else:
                print("ошибка ввода")
                break
            finally:
                if container is not None:
                    print("Поток заверешен корректно")
                    container.close()

        print("✅ Поток PyAV завершён")

    def stop(self):
        self._run_flag = False
        self.wait()


def get_img_sync(camera_path: str = None):
    """Синхронная версия для RTSP камеры"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if camera_path:
            result = loop.run_until_complete(get_img_PyAV(camera_path))
        else:
            result = loop.run_until_complete(get_img_PyAV())
        loop.close()
        return result
    except Exception as e:
        print(f"❌ Ошибка получения фото: {e}")
        return None


async def get_img_PyAV(camera_path:str = "rtsp://admin:@192.168.0.27:554/h264?tcp"):
    try:
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

        result_image_name = save_image(img)
        return result_image_name

async def camera_test(camera_path: str = "rtsp://admin:@192.168.0.27:554/h264?tcp"):
    try:
        # Опции для стабильности
        print("📡 Попытка подключения к IP-камере...")
        av.open(camera_path)
        return True
    except Exception as e:
        print(f"❌ Не удалось подключиться к камере, Ошибка: {e}")
        return False

def save_image(captured_image):
    filecount = 0
    for file in os.listdir(PHOTO_DIR):
        if f"{FILE_NAME}{date.today()}" in file:
            filecount += 1
    if filecount == 0:
        result_image_name = f"{PHOTO_DIR + FILE_NAME}{date.today()}.{FILE_EXTENSION}"
    else:
        result_image_name = f"{PHOTO_DIR + FILE_NAME}{date.today()}_{filecount}.{FILE_EXTENSION}"

    captured_image.to_image().save(result_image_name)
    print(f"кадр сохранен, {result_image_name} ")
    return result_image_name


if __name__ == '__main__':
    asyncio.run(get_img_PyAV())