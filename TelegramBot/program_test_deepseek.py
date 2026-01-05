#!/usr/db/env python3
"""
🚀 СИСТЕМА ДЕБАГА ПАРКОВОЧНОЙ СИСТЕМЫ
Запуск: python debug.py [команда]
"""

import sys
import os
import time
from pathlib import Path

# Добавляем пути
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "TelegramBot"))


def print_header(text):
    """Красивый заголовок"""
    print("\n" + "=" * 60)
    print(f"🚀 {text}")
    print("=" * 60)


def print_section(text):
    """Раздел"""
    print(f"\n📌 {text}")
    print("-" * 40)


def test_imports():
    """Тест импортов"""
    print_header("ТЕСТ ИМПОРТОВ")

    modules_to_test = [
        ("TelegramBot.logs.logic", "Logic модуль"),
        ("TelegramBot.logs.detector", "Detector модуль"),
        ("ultralytics", "YOLO библиотека"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
    ]

    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: успешно")
        except ImportError as e:
            print(f"❌ {description}: {e}")
        except Exception as e:
            print(f"⚠️  {description}: {type(e).__name__} - {e}")


def test_model_cache():
    """Тест кеша модели"""
    print_header("ТЕСТ КЕША МОДЕЛИ")

    try:
        from TelegramBot import logic

        print_section("Первый вызов (должен загрузить)")
        #start = time.time()
        model1 = logic.get_model()
        #time1 = time.time() - start
       # print(f"   Время: {time1:.2f} сек")
        print(f"   Модель: {model1}")

        print_section("Второй вызов (должен взять из кеша)")
        #start = time.time()
        model2 = logic.get_model()
        #time2 = time.time() - start
        #print(f"   Время: {time2:.2f} сек")
        print(f"   Модель: {model2}")

        print_section("Сравнение")
        print(f"   Один объект?: {model1 is model2}")
        print(f"   Ускорение: {time1 / time2:.1f} раз")

        if model1 is model2:
            print("✅ КЕШ РАБОТАЕТ!")
        else:
            print("❌ КЕШ НЕ РАБОТАЕТ - разные объекты!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def test_detection():
    """Тест детекции"""
    print_header("ТЕСТ ДЕТЕКЦИИ")

    try:
        from TelegramBot import detector

        print_section("Запуск детекции")
        start = time.time()

        # Проверяем разные изображения
        test_images = ["test3.jpg", "test4.jpg", "test5.jpg"]

        for img in test_images:
            img_path = project_root / "img" / "input" / img
            if img_path.exists():
                print(f"\n📸 Обработка {img}:")

                # Сначала загружаем модель
                detector.start()

                # Запускаем детекцию
                result = detector.check_auto(
                    save="Отладка1.mask",
                    processed_image=img
                )

                if result:
                    occupied, free = result
                    print(f"   Занято: {len(occupied)}, Свободно: {len(free)}")
                else:
                    print("   ❌ Нет результата")
            else:
                print(f"⚠️  Изображение не найдено: {img}")

        total_time = time.time() - start
        print(f"\n⏱️  Общее время: {total_time:.2f} сек")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def test_file_structure():
    """Проверка структуры файлов"""
    print_header("СТРУКТУРА ФАЙЛОВ")

    required_files = [
        ("backup/yolov8x.pt", "Модель YOLO", True),
        ("img/input/test3.jpg", "Тестовое изображение", False),
        ("saves/Отладка1.mask", "Сохранение парковки", False),
        ("TelegramBot/logs/logic.py", "Логика", True),
        ("TelegramBot/logs/detector.py", "Детектор", True),
    ]

    for path, description, critical in required_files:
        file_path = project_root / path
        exists = file_path.exists()
        icon = "✅" if exists else "❌"

        if not exists and critical:
            status = "КРИТИЧЕСКИ!"
        elif not exists:
            status = "не найден"
        else:
            status = f"найден ({file_path.stat().st_size / 1024 / 1024:.1f} MB)"

        print(f"{icon} {description}: {status}")


def check_model_path():
    """Проверка пути к модели"""
    print_header("ПУТЬ К МОДЕЛИ")

    try:
        from TelegramBot import logic

        print_section("Текущие пути")
        print(f"   Рабочая директория: {os.getcwd()}")
        print(f"   Путь к logic.py: {logic.__file__}")

        if hasattr(logic, 'MODELPATH'):
            print(f"   MODELPATH в logic: {logic.MODELPATH}")
            print(f"   Абсолютный путь: {os.path.abspath(logic.MODELPATH)}")
            print(f"   Существует: {os.path.exists(os.path.abspath(logic.MODELPATH))}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def module_diagnostics():
    """Диагностика модулей"""
    print_header("ДИАГНОСТИКА МОДУЛЕЙ")

    print_section("Импортированные модули")
    for key in sorted(sys.modules.keys()):
        if any(x in key for x in ['logic', 'detector', 'algorithm', 'TelegramBot']):
            module = sys.modules[key]
            print(f"   {key}:")
            print(f"     ID: {id(module)}")
            if hasattr(module, '__file__'):
                print(f"     Файл: {module.__file__}")

    print_section("Пути поиска Python")
    for i, path in enumerate(sys.path[:10]):  # первые 10
        print(f"   [{i}] {path}")


def test_bot_import():
    """Тест импорта бота"""
    print_header("ТЕСТ БОТА")

    try:
        from TelegramBot import tgbot
        print("✅ Модуль бота загружен")

        # Проверяем основные компоненты
        components = ['bot', 'dp', 'storage']
        for comp in components:
            if hasattr(tgbot, comp):
                print(f"✅ {comp}: найден")
            else:
                print(f"⚠️  {comp}: не найден")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def run_performance_test():
    """Тест производительности"""
    print_header("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")

    try:
        from TelegramBot import detector

        print_section("Первая детекция (с загрузкой модели)")
        start = time.time()
        detector.start()  # Предзагрузка
        time1 = time.time() - start
        print(f"   Время инициализации: {time1:.2f} сек")

        print_section("Последующие детекции (только инференс)")
        times = []

        for i in range(3):
            start = time.time()
            result = detector.check_auto(
                save="Отладка1.mask",
                processed_image="test3.jpg"
            )
            times.append(time.time() - start)

            if result:
                occupied, free = result
                print(f"   Попытка {i + 1}: {times[-1]:.2f} сек, машин: {len(occupied)}")

        print_section("Результаты")
        print(f"   Первый вызов: {time1:.2f} сек")
        print(f"   Среднее последующих: {sum(times) / len(times):.2f} сек")
        print(f"   Ускорение: {time1 / (sum(times) / len(times)):.1f} раз")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def save_debug_report():
    """Сохранение отчета"""
    import io
    from datetime import datetime

    print_header("СОХРАНЕНИЕ ОТЧЕТА")

    # Захватываем вывод
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        # Запускаем все тесты
        test_imports()
        test_model_cache()
        test_file_structure()
        check_model_path()
        module_diagnostics()
        run_performance_test()

        # Возвращаем stdout
        sys.stdout = old_stdout

        # Сохраняем в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = project_root / f"debug_report_{timestamp}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(buffer.getvalue())

        print(f"✅ Отчет сохранен: {report_file}")

        # Показываем кратко
        print("\n📋 КРАТКИЙ ОТЧЕТ:")
        with open(report_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if any(marker in line for marker in ['✅', '❌', '⚠️', '🚀', '📌']):
                    print(line.rstrip())

    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ Ошибка сохранения отчета: {e}")


def interactive_debug():
    """Интерактивный дебаг"""
    print_header("ИНТЕРАКТИВНЫЙ ДЕБАГ")

    tests = {
        '1': ("Проверка импортов", test_imports),
        '2': ("Тест кеша модели", test_model_cache),
        '3': ("Тест детекции", test_detection),
        '4': ("Структура файлов", test_file_structure),
        '5': ("Путь к модели", check_model_path),
        '6': ("Диагностика модулей", module_diagnostics),
        '7': ("Тест бота", test_bot_import),
        '8': ("Тест производительности", run_performance_test),
        '9': ("Полный отчет", save_debug_report),
        '0': ("Выход", None),
    }

    while True:
        print("\n📋 ВЫБЕРИТЕ ТЕСТ:")
        for key, (name, _) in tests.items():
            print(f"  [{key}] {name}")

        choice = input("\nВаш выбор (или Enter для выхода): ").strip()

        if not choice or choice == '0':
            break

        if choice in tests:
            name, func = tests[choice]
            print(f"\n▶️  Запуск: {name}")
            if func:
                func()
        else:
            print("❌ Неверный выбор")


def main():
    """Главная функция"""
    print_header("СИСТЕМА ДЕБАГА ПАРКОВОЧНОГО ПРОЕКТА")
    print("Версия: 1.0")
    print(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "full":
            test_imports()
            test_model_cache()
            test_detection()
            test_file_structure()
            check_model_path()
            module_diagnostics()
            test_bot_import()
            run_performance_test()
        elif command == "cache":
            test_model_cache()
        elif command == "imports":
            test_imports()
        elif command == "detect":
            test_detection()
        elif command == "report":
            save_debug_report()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("Доступные команды: full, cache, imports, detect, report")
    else:
        interactive_debug()

    print_header("ДЕБАГ ЗАВЕРШЕН")


if __name__ == "__main__":
    main()