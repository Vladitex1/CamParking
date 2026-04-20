import cv2
from datetime import date
import asyncio
import av
import os
from PySide6.QtCore import *
from PySide6.QtGui import QImage
from Editor.prod.data.signal_bus import signal
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
        container = None
        options = {
            'rtsp_transport': 'udp',
            'fflags': 'nobuffer',
            'flags': 'low_delay',
            'probesize': '32',
            'analyzeduration': '0',
            'max_delay': '0'
        }

        print(f"🚀 [1/6] Запуск потока подключения...")
        print(f"📡 [2/6] URL: {self.url}")
        print(f"📐 [3/6] Целевое разрешение: {self.target_size[0]}x{self.target_size[1]}")

        while self._run_flag:
            try:
                print(f"🔗 [4/6] Попытка открытия RTSP потока...")
                container = av.open(self.url, options=options, timeout=5)
                print(f"✅ [5/6] RTSP поток открыт успешно")

                stream = container.streams.video[0]
                stream.thread_type = 'AUTO'
                print(f"🎥 [6/6] Видеопоток получен, начинаю захват кадров...")
                print(f"📹 Статус: АКТИВЕН ✅")
                signal.camera_ready.emit(True)

                for packet in container.demux(stream):
                    if not self._run_flag:
                        print("⏹️ Получен сигнал остановки потока")
                        break

                    for frame in packet.decode():
                        if not self._run_flag:
                            break

                        img = frame.to_ndarray(format='rgb24')

                        if (img.shape[1], img.shape[0]) != self.target_size:
                            img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_LINEAR)

                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        self.change_pixmap_signal.emit(qt_image)

                print("📴 Статус: ОТКЛЮЧЕН (поток завершён)")

            except TimeoutError:
                print("❌ Статус: ОШИБКА — таймаут подключения (5 секунд)")
                signal.camera_thread_end_request.emit(False)
                break
            except av.error.ConnectionRefusedError:
                print("❌ Статус: ОШИБКА — соединение отклонено")
                signal.camera_thread_end_request.emit(False)
                break
            except av.error.HTTPUnauthorizedError:
                print("❌ Статус: ОШИБКА — неверный логин или пароль (401)")
                signal.camera_thread_end_request.emit(False)
                break
            except av.error.InvalidDataError:
                print("❌ Статус: ОШИБКА — неверные данные потока")
                signal.camera_thread_end_request.emit(False)
                break
            except av.FFmpegError as e:
                print(f"❌ Статус: ОШИБКА FFmpeg — {e}")
                signal.camera_thread_end_request.emit(False)
                break
            except Exception as e:
                print(f"❌ Статус: НЕИЗВЕСТНАЯ ОШИБКА — {type(e).__name__}: {e}")
                signal.camera_thread_end_request.emit(False)
                break
            finally:
                if container is not None:
                    print("🔒 Закрытие контейнера...")
                    container.close()
                    print("✅ Контейнер закрыт")

            # Если вышли из цикла demux но _run_flag ещё True — переподключаемся
            if self._run_flag:
                print("🔄 Повторная попытка подключения через 3 секунды...")
                self.msleep(3000)

        signal.camera_thread_end_request.emit(False)
        print("🛑 Поток CameraThread полностью завершён")

    def stop(self):
        self._run_flag = False
        signal.camera_thread_end_request.emit(False)


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


async def get_img_PyAV(camera_path:str = None,out_data_type:str = "path"):
    if camera_path == None:
        camera_path = "rtsp://admin:@192.168.0.27:554/h264?tcp"

    options = {
    'skip_frame': 'default',           # Пропускать неключевые кадры
    'threads': '1',                    # Кол-во потоков декодера
    'refcounted_frames': '1',          # Счетчик ссылок на кадры
    'lowres': '0',                     # 0=полное разрешение, 1=1/2, 2=1/4
    }

    print("📡 Попытка подключения к IP-камере...")
    try:
        print(f"🔗 Попытка открытия RTSP потока...")
        container = av.open(camera_path, options=options, timeout=5)
    except Exception as e:
        print(f"❌ Не удалось подключиться к камере, Ошибка: {e}")
        return 0
    print("Успешная попытка.")
    result = None
    try:
        for index, frame in enumerate(container.decode(video=0)):
            result = frame
            break
    except Exception as e:
        print(f"Ошибка в декодировании {e}")
        return 0

    print("📸 Делаю фото...")

    if result is not None:
        if isinstance(result, list) and len(result) > 1:
            img = result[1]
        else:
            img = result
        print("✅ Фото получено")

        match out_data_type:
            case "data":
                return img.to_ndarray(format='rgb24')
            case "path":
                return save_image(img)#result_image_name =
            case _:
                return 0
    else:
        print("Результат захвата изображения не найден")
        return 0


async def camera_test(camera_path: str = "rtsp://admin:@192.168.0.27:554/h264?tcp"):
    options = {
        'skip_frame': 'default',  # Пропускать неключевые кадры
        'threads': '1',  # Кол-во потоков декодера
        'refcounted_frames': '1',  # Счетчик ссылок на кадры
        'lowres': '0',  # 0=полное разрешение, 1=1/2, 2=1/4
    }
    print("📡 Попытка подключения к IP-камере...")
    try:
        print(f"🔗 Попытка открытия RTSP потока...")
        container = av.open(camera_path, options=options, timeout=5)
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