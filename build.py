#!/usr/bin/env python3
"""
Скрипт для сборки приложения в EXE файл
Использует PyInstaller для создания исполняемого файла
Улучшенная версия с подробным выводом ошибок
"""

import subprocess
import sys
import os
import traceback
import shutil


def print_header():
    """Вывод заголовка"""
    print("\n" + "=" * 70)
    print("🖥️  System Monitor - Сборщик EXE (Улучшенная версия)")
    print("=" * 70)
    print()


def print_error(message):
    """Вывод сообщения об ошибке"""
    print(f"\n❌ ОШИБКА: {message}")
    print()


def print_success(message):
    """Вывод сообщения об успехе"""
    print(f"\n✅ УСПЕХ: {message}")
    print()


def install_dependencies():
    """Установка необходимых зависимостей"""
    print("📦 Установка зависимостей...")
    print("-" * 70)
    
    dependencies = ['psutil', 'pyinstaller']
    
    for dep in dependencies:
        print(f"\n[1/2] Установка {dep}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dep, "--upgrade"],
                capture_output=False,
                check=True
            )
            if result.returncode == 0:
                print(f"✅ {dep} установлен успешно")
            else:
                print_error(f"Не удалось установить {dep}")
                return False
        except subprocess.CalledProcessError as e:
            print_error(f"Ошибка при установке {dep}: {e}")
            print("Попробуйте запустить от имени администратора или проверьте подключение к интернету")
            return False
        except Exception as e:
            print_error(f"Неожиданная ошибка при установке {dep}: {e}")
            traceback.print_exc()
            return False
    
    print_success("Все зависимости установлены")
    return True


def check_files():
    """Проверка наличия необходимых файлов"""
    print("\n🔍 Проверка файлов...")
    print("-" * 70)
    
    required_files = ['app.py', 'core.py']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Файл найден: {file}")
        else:
            print(f"❌ Файл не найден: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Отсутствуют файлы: {', '.join(missing_files)}")
        print("Убедитесь, что вы запускаете сборщик из корневой папки проекта")
        return False
    
    print_success("Все файлы найдены")
    return True


def build_exe(console_mode=False):
    """Сборка EXE файла с помощью PyInstaller"""
    print("\n🔨 Начало сборки EXE файла...")
    print("-" * 70)
    
    # Проверка файлов перед сборкой
    if not check_files():
        return False
    
    # Определение типа сборки
    build_type = "Консольная версия (для отладки)" if console_mode else "GUI версия (без консоли)"
    print(f"Тип сборки: {build_type}")
    
    # Команда для PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Один файл
        "--name", "SystemMonitor",      # Имя приложения
        "--clean",                      # Очистка перед сборкой
    ]
    
    if not console_mode:
        cmd.append("--windowed")        # Без консоли (для GUI)
        print("Режим: GUI (окно без консоли)")
    else:
        print("Режим: Консоль (видно логи и ошибки)")
    
    # Добавление ядра как данных
    if os.name != 'nt':
        cmd.extend(["--add-data", "core.py:."])
    else:
        cmd.extend(["--add-data", "core.py;."])
    
    cmd.append("app.py")  # Главный файл
    
    print(f"\nКоманда: {' '.join(cmd)}")
    print("\n" + "-" * 70)
    print("Процесс сборки (может занять несколько минут):")
    print("-" * 70)
    
    try:
        # Запуск сборки с выводом в реальном времени
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print_success("Сборка завершена успешно!")
            print("=" * 70)
            
            exe_name = "SystemMonitor.exe" if os.name == 'nt' else "SystemMonitor"
            exe_path = os.path.join("dist", exe_name)
            
            if os.path.exists(exe_path):
                exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # Размер в МБ
                print(f"\n📁 Путь к файлу: {os.path.abspath(exe_path)}")
                print(f"📊 Размер файла: {exe_size:.2f} MB")
                
                if os.name == 'nt':
                    print("\n💡 Для запуска откройте: dist\\SystemMonitor.exe")
                else:
                    print("\n💡 Для запуска откройте: dist/SystemMonitor")
                    print("   Или выполните: chmod +x dist/SystemMonitor && ./dist/SystemMonitor")
            else:
                print_warning("EXE файл не найден в ожидаемом месте")
            
            return True
        else:
            print_error(f"PyInstaller завершился с кодом ошибки: {result.returncode}")
            print("\nВозможные причины:")
            print("  1. Отсутствуют зависимости (выполните опцию 1)")
            print("  2. Проблемы с правами доступа (запустите от администратора)")
            print("  3. Антивирус блокирует создание EXE")
            print("  4. Недостаточно места на диске")
            return False
            
    except FileNotFoundError:
        print_error("PyInstaller не найден. Установите его: pip install pyinstaller")
        return False
    except Exception as e:
        print_error(f"Неожиданная ошибка при сборке: {e}")
        print("\nПодробная информация об ошибке:")
        traceback.print_exc()
        return False


def build_console_version():
    """Сборка версии с консолью (для отладки)"""
    print("\n🔨 Сборка консольной версии (для отладки)...")
    print("Эта версия будет показывать все ошибки и логи в консоли")
    return build_exe(console_mode=True)


def clean_build():
    """Очистка временных файлов сборки"""
    print("\n🧹 Очистка временных файлов...")
    print("-" * 70)
    
    folders_to_remove = ['build', '__pycache__', 'dist']
    files_to_remove = ['SystemMonitor.spec', 'SystemMonitor_debug.spec']
    
    removed_count = 0
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"✅ Удалена папка: {folder}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Не удалось удалить папку {folder}: {e}")
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Удален файл: {file}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Не удалось удалить файл {file}: {e}")
    
    if removed_count > 0:
        print_success(f"Очистка завершена. Удалено объектов: {removed_count}")
    else:
        print("ℹ️ Нечего очищать (временные файлы не найдены)")
    
    return True


def test_application():
    """Тестирование приложения перед сборкой"""
    print("\n🧪 Тестирование приложения...")
    print("-" * 70)
    
    # Сначала тестируем ядро
    print("\n[1/3] Тестирование ядра (core.py)...")
    try:
        from core import SystemCore
        core = SystemCore()
        data = core.get_all_data()
        print(f"✅ Ядро работает. Система: {data['system']['system']}")
        print(f"   CPU: {data['cpu']['usage_percent']}%")
        print(f"   RAM: {data['memory']['percent']}%")
    except ImportError as e:
        print_error(f"Не удалось импортировать ядро: {e}")
        print("Установите зависимости: pip install psutil")
        return False
    except Exception as e:
        print_error(f"Ошибка ядра: {e}")
        traceback.print_exc()
        return False
    
    # Тестируем наличие tkinter
    print("\n[2/3] Проверка tkinter...")
    try:
        import tkinter as tk
        print("✅ Tkinter доступен")
    except ImportError as e:
        print_error(f"Tkinter не найден: {e}")
        print("На Windows: tkinter встроен в Python")
        print("На Linux: установите python3-tk (sudo apt install python3-tk)")
        return False
    
    # Пробуем импортировать приложение (без запуска GUI)
    print("\n[3/3] Проверка приложения (app.py)...")
    try:
        import app
        print("✅ Приложение импортируется корректно")
    except Exception as e:
        print_error(f"Ошибка импорта приложения: {e}")
        traceback.print_exc()
        return False
    
    print_success("Все тесты пройдены! Приложение готово к сборке.")
    print("\n💡 Теперь можете запустить приложение:")
    print("   python app.py")
    print("   или собрать в EXE (опция 1 или 2)")
    return True


def print_warning(message):
    """Вывод предупреждения"""
    print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЕ: {message}")
    print()


def wait_for_exit():
    """Пауза перед выходом"""
    print("\n" + "=" * 70)
    input("Нажмите Enter для выхода...")


def main_menu():
    """Основное меню с циклом"""
    while True:
        print_header()
        
        print("Выберите действие:")
        print("  1. Установить зависимости и собрать EXE")
        print("  2. Только собрать EXE (зависимости уже установлены)")
        print("  3. Собрать консольную версию (для отладки ошибок)")
        print("  4. Очистить временные файлы")
        print("  5. 🧪 Тестировать приложение перед сборкой")
        print("  6. Выйти")
        print()
        
        choice = input("Ваш выбор (1-6): ").strip()
        
        if choice == '1':
            if install_dependencies():
                build_exe()
            else:
                print("\n⚠️ Установка зависимостей не удалась. Попробуйте:")
                print("   1. Запустить терминал от имени администратора")
                print("   2. Проверить подключение к интернету")
                print("   3. Выполнить вручную: pip install psutil pyinstaller")
        
        elif choice == '2':
            build_exe()
        
        elif choice == '3':
            build_console_version()
        
        elif choice == '4':
            clean_build()
        
        elif choice == '5':
            test_application()
        
        elif choice == '6':
            print("\n👋 До свидания!")
            break
        
        else:
            print_error("Неверный выбор. Введите число от 1 до 6.")
        
        # Пауза чтобы пользователь мог увидеть результат
        if choice != '6':
            wait_for_exit()


def main():
    """Точка входа"""
    try:
        # Проверка версии Python
        if sys.version_info < (3, 6):
            print_error(f"Требуется Python 3.6 или выше. У вас: {sys.version}")
            wait_for_exit()
            sys.exit(1)
        
        print(f"Python версия: {sys.version}")
        print(f"Python путь: {sys.executable}")
        print(f"Рабочая директория: {os.getcwd()}")
        
        # Запуск основного меню
        main_menu()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем (Ctrl+C)")
        wait_for_exit()
    except Exception as e:
        print_error(f"Критическая ошибка: {e}")
        print("\nПодробная трассировка:")
        traceback.print_exc()
        wait_for_exit()
        sys.exit(1)


if __name__ == "__main__":
    main()
