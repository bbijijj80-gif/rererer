#!/usr/bin/env python3
"""
Скрипт для сборки приложения в EXE файл
Использует PyInstaller для создания исполняемого файла
"""

import subprocess
import sys
import os


def install_dependencies():
    """Установка необходимых зависимостей"""
    print("📦 Установка зависимостей...")
    
    dependencies = ['psutil', 'pyinstaller']
    
    for dep in dependencies:
        print(f"Установка {dep}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✅ Зависимости установлены\n")


def build_exe():
    """Сборка EXE файла с помощью PyInstaller"""
    print("🔨 Сборка EXE файла...")
    
    # Команда для PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Один файл
        "--windowed",                   # Без консоли (для GUI)
        "--name", "SystemMonitor",      # Имя приложения
        "--icon=NONE",                  # Без иконки (можно добавить свою)
        "--add-data", "core.py;.",      # Включение ядра
        "app.py"                        # Главный файл
    ]
    
    # Для Linux/Mac используем другой разделитель путей
    if os.name != 'nt':
        cmd[8] = "--add-data"
        cmd[9] = "core.py:."
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Сборка завершена успешно!")
        print("\n📁 EXE файл находится в папке: dist/SystemMonitor.exe")
        
        if os.name == 'nt':
            print("\n💡 Для запуска просто откройте dist/SystemMonitor.exe")
        else:
            print("\n💡 Для запуска откройте dist/SystemMonitor")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка сборки: {e}")
        return False
    
    return True


def build_console_version():
    """Сборка версии с консолью (для отладки)"""
    print("🔨 Сборка консольной версии (для отладки)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "SystemMonitor_debug",
        "app.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Консольная версия собрана: dist/SystemMonitor_debug.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка сборки: {e}")


def clean_build():
    """Очистка временных файлов сборки"""
    print("🧹 Очистка временных файлов...")
    
    folders_to_remove = ['build', '__pycache__']
    files_to_remove = ['SystemMonitor.spec']
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"Удалена папка: {folder}")
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Удален файл: {file}")
    
    print("✅ Очистка завершена\n")


def main():
    """Основная функция"""
    print("=" * 60)
    print("🖥️  System Monitor - Сборщик EXE")
    print("=" * 60)
    print()
    
    # Проверка Python
    print(f"Python версия: {sys.version}")
    print(f"Python путь: {sys.executable}")
    print()
    
    # Меню
    print("Выберите действие:")
    print("1. Установить зависимости и собрать EXE")
    print("2. Только собрать EXE (зависимости уже установлены)")
    print("3. Собрать консольную версию (для отладки)")
    print("4. Очистить временные файлы")
    print("5. Выйти")
    print()
    
    choice = input("Ваш выбор (1-5): ").strip()
    
    if choice == '1':
        install_dependencies()
        build_exe()
    elif choice == '2':
        build_exe()
    elif choice == '3':
        build_console_version()
    elif choice == '4':
        clean_build()
    elif choice == '5':
        print("\n👋 До свидания!")
        sys.exit(0)
    else:
        print("\n❌ Неверный выбор")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Сборка завершена!")
    print("=" * 60)


if __name__ == "__main__":
    main()
