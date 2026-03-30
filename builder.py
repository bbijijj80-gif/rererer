#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor - Сборщик EXE (Улучшенная версия)
Интерактивный сборщик приложения с тестированием и обработкой ошибок
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    """Цвета для терминала"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def print_header(text):
    """Вывод заголовка"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")


def print_success(text):
    """Вывод успешного сообщения"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Вывод ошибки"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Вывод информации"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")


def check_python():
    """Проверка наличия Python"""
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except Exception:
        pass
    
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except Exception:
        pass
    
    return False, "Python не найден"


def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = ['psutil', 'pyinstaller']
    missing = []
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            missing.append(package)
    
    return len(missing) == 0, missing


def install_dependencies():
    """Установка зависимостей"""
    print_info("Установка зависимостей...")
    
    packages = ['psutil', 'pyinstaller']
    
    for package in packages:
        print(f"  Установка {package}...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package, '--quiet'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success(f"{package} установлен")
            else:
                print_error(f"Ошибка установки {package}: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"Ошибка при установке {package}: {str(e)}")
            return False
    
    return True


def verify_files():
    """Проверка наличия всех необходимых файлов"""
    print_header("🔍 Проверка целостности файлов")
    
    required_files = {
        'core.py': 'Ядро мониторинга системы',
        'gui.py': 'Графический интерфейс',
        'app.py': 'Главное приложение (точка входа)',
        'builder.py': 'Сборщик EXE (этот файл)'
    }
    
    all_exist = True
    
    for filename, description in required_files.items():
        filepath = Path(filename)
        if filepath.exists():
            print_success(f"{filename} - {description}")
            
            # Проверка размера файла (не должен быть пустым)
            if filepath.stat().st_size == 0:
                print_error(f"  Файл {filename} пустой!")
                all_exist = False
            else:
                print_info(f"  Размер: {filepath.stat().st_size} байт")
        else:
            print_error(f"{filename} - {description} - ОТСУТСТВУЕТ")
            all_exist = False
    
    # Проверка содержимого core.py
    if Path('core.py').exists():
        try:
            with open('core.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SystemMonitorCore' not in content:
                    print_error("core.py не содержит класс SystemMonitorCore!")
                    all_exist = False
                if 'psutil' not in content:
                    print_error("core.py не импортирует psutil!")
                    all_exist = False
        except Exception as e:
            print_error(f"Ошибка чтения core.py: {e}")
            all_exist = False
    
    # Проверка содержимого gui.py
    if Path('gui.py').exists():
        try:
            with open('gui.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SystemMonitorGUI' not in content:
                    print_error("gui.py не содержит класс SystemMonitorGUI!")
                    all_exist = False
                if 'tkinter' not in content:
                    print_error("gui.py не импортирует tkinter!")
                    all_exist = False
        except Exception as e:
            print_error(f"Ошибка чтения gui.py: {e}")
            all_exist = False
    
    # Проверка содержимого app.py
    if Path('app.py').exists():
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SystemMonitorCore' not in content or 'SystemMonitorGUI' not in content:
                    print_error("app.py не импортирует необходимые модули!")
                    all_exist = False
                if 'main()' not in content:
                    print_error("app.py не содержит функцию main()!")
                    all_exist = False
        except Exception as e:
            print_error(f"Ошибка чтения app.py: {e}")
            all_exist = False
    
    return all_exist


def test_core():
    """Тестирование ядра"""
    print_header("🧪 Тестирование ядра мониторинга")
    
    try:
        print_info("Запуск теста ядра...")
        result = subprocess.run(
            [sys.executable, 'core.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("Ядро работает корректно!")
            
            # Проверяем вывод
            if 'System Monitor Core' in result.stdout:
                print_success("Получены данные о системе")
            
            if Path('system_report.json').exists():
                print_success("JSON отчет создан")
                
                # Проверка размера JSON
                size = Path('system_report.json').stat().st_size
                if size > 100:
                    print_success(f"Размер отчета: {size} байт")
                else:
                    print_warning("Отчет слишком маленький")
            
            return True
        else:
            print_error("Ошибка при тестировании ядра!")
            print(f"\n{Colors.RED}Вывод ошибок:{Colors.RESET}")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Таймаут при тестировании ядра (>30 сек)")
        return False
    except Exception as e:
        print_error(f"Исключение при тестировании: {str(e)}")
        return False


def test_gui():
    """Тестирование GUI (базовая проверка)"""
    print_header("🧪 Тестирование графического интерфейса")
    
    try:
        print_info("Проверка синтаксиса gui.py...")
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'gui.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Синтаксис gui.py корректен")
            
            # Проверка импортов
            print_info("Проверка импортов...")
            test_code = """
import sys
try:
    import tkinter
    print("tkinter: OK")
except ImportError as e:
    print(f"tkinter: ERROR - {e}")
    sys.exit(1)

try:
    from core import SystemMonitorCore
    print("core module: OK")
except ImportError as e:
    print(f"core module: ERROR - {e}")
    sys.exit(1)

print("Все импорты успешны")
"""
            result = subprocess.run(
                [sys.executable, '-c', test_code],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print_success("GUI готов к использованию")
                print_warning("Для полноценного теста требуется графическая среда (X11)")
                return True
            else:
                print_error("Ошибка импортов GUI")
                return False
        else:
            print_error("Синтаксическая ошибка в gui.py!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Исключение при тестировании GUI: {str(e)}")
        return False


def run_full_test():
    """Полное тестирование перед сборкой"""
    print_header("🧪 Полное тестирование приложения")
    
    tests_passed = 0
    total_tests = 3
    
    # Тест 1: Проверка файлов
    print("\n[Тест 1/3] Проверка файлов...")
    if verify_files():
        tests_passed += 1
    
    # Тест 2: Тест ядра
    print("\n[Тест 2/3] Тестирование ядра...")
    if test_core():
        tests_passed += 1
    
    # Тест 3: Тест GUI
    print("\n[Тест 3/3] Тестирование GUI...")
    if test_gui():
        tests_passed += 1
    
    # Результаты
    print_header("📊 Результаты тестирования")
    print(f"Пройдено тестов: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print_success("Все тесты пройдены! Можно собирать EXE.")
        return True
    elif tests_passed >= total_tests // 2:
        print_warning("Часть тестов пройдена. Сборка возможна, но могут быть проблемы.")
        return True
    else:
        print_error("Критические ошибки! Устраните проблемы перед сборкой.")
        return False


def build_exe(console_mode=False):
    """Сборка EXE файла"""
    print_header("🔨 Сборка EXE приложения")
    
    # Проверка наличия PyInstaller
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error("PyInstaller не установлен!")
            print_info("Запустите опцию 1 для установки зависимостей")
            return False
    except Exception:
        print_error("PyInstaller не найден!")
        return False
    
    # Проверка наличия всех необходимых файлов
    print_info("Проверка файлов проекта...")
    required_files = ['app.py', 'core.py', 'gui.py']
    missing_files = []
    
    for filename in required_files:
        if not Path(filename).exists():
            missing_files.append(filename)
    
    if missing_files:
        print_error(f"Отсутствуют файлы: {', '.join(missing_files)}")
        print_error("Убедитесь, что вы запускаете сборщик из корневой папки проекта")
        return False
    
    print_success("Все файлы найдены")
    
    # Подготовка команды
    spec_name = 'SystemMonitor'
    
    # Удаляем старые файлы сборки
    for folder in ['build', 'dist']:
        if Path(folder).exists():
            print_info(f"Очистка папки {folder}...")
            shutil.rmtree(folder)
    
    # Формируем команду PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', spec_name,
        '--onefile',
        '--windowed' if not console_mode else '--console',
        '--add-data', 'core.py;.' if os.name == 'nt' else '--add-data', 'core.py:.',
        '--hidden-import', 'psutil',
        '--hidden-import', 'tkinter',
        '--icon', 'NONE',
        '--clean',
        '--noconfirm',
        'app.py'
    ]
    
    print_info("Команда сборки:")
    print(f"  {' '.join(cmd)}\n")
    
    try:
        print_info("Запуск сборки...")
        print("(Это может занять несколько минут)\n")
        
        result = subprocess.run(
            cmd,
            capture_output=False,  # Показываем вывод в реальном времени
            text=True
        )
        
        if result.returncode == 0:
            print_success("Сборка завершена успешно!")
            
            # Проверка результата
            exe_path = Path('dist') / f'{spec_name}.exe' if os.name == 'nt' else Path('dist') / spec_name
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print_success(f"EXE файл создан: {exe_path}")
                print_info(f"Размер: {size_mb:.2f} MB")
                
                # Копируем core.py рядом с exe для надежности
                core_dest = Path('dist') / 'core.py'
                shutil.copy('core.py', core_dest)
                print_info("core.py скопирован в папку dist")
                
                return True
            else:
                print_error("EXE файл не найден после сборки!")
                return False
        else:
            print_error("Ошибка при сборке!")
            print_error("Смотрите вывод выше для деталей")
            return False
            
    except KeyboardInterrupt:
        print_error("\nСборка прервана пользователем")
        return False
    except Exception as e:
        print_error(f"Исключение при сборке: {str(e)}")
        return False


def clean_build_files():
    """Очистка временных файлов сборки"""
    print_header("🧹 Очистка временных файлов")
    
    folders_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['system_report.json']
    
    cleaned_count = 0
    
    for folder in folders_to_clean:
        folder_path = Path(folder)
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
                print_success(f"Удалена папка: {folder}")
                cleaned_count += 1
            except Exception as e:
                print_error(f"Не удалось удалить {folder}: {e}")
        else:
            print_info(f"Папка {folder} не найдена")
    
    for file in files_to_clean:
        file_path = Path(file)
        if file_path.exists():
            try:
                file_path.unlink()
                print_success(f"Удален файл: {file}")
                cleaned_count += 1
            except Exception as e:
                print_error(f"Не удалось удалить {file}: {e}")
    
    print_info(f"Всего очищено объектов: {cleaned_count}")


def main_menu():
    """Главное меню"""
    while True:
        print_header("🖥️  System Monitor - Сборщик EXE (Улучшенная версия)")
        
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
            # Установка и сборка
            print_header("📦 Установка зависимостей и сборка")
            
            if install_dependencies():
                print_success("Зависимости установлены")
                
                if run_full_test():
                    print_info("\nПереход к сборке...\n")
                    build_exe(console_mode=False)
                else:
                    print_error("\nТестирование не пройдено. Сборка отменена.")
            else:
                print_error("Не удалось установить зависимости")
            
            input("\nНажмите Enter для продолжения...")
            
        elif choice == '2':
            # Только сборка
            print_header("🔨 Сборка EXE")
            
            deps_ok, missing = check_dependencies()
            if deps_ok:
                if run_full_test():
                    build_exe(console_mode=False)
                else:
                    print_warning("\nТестирование показало проблемы. Продолжить сборку?")
                    cont = input("Продолжить? (y/n): ").strip().lower()
                    if cont == 'y':
                        build_exe(console_mode=False)
            else:
                print_error(f"Отсутствуют зависимости: {', '.join(missing)}")
                print_info("Выберите опцию 1 для установки")
            
            input("\nНажмите Enter для продолжения...")
            
        elif choice == '3':
            # Консольная версия
            print_header("🖥️  Сборка консольной версии")
            
            deps_ok, _ = check_dependencies()
            if deps_ok:
                print_warning("Консольная версия будет показывать отладочную информацию")
                cont = input("Продолжить? (y/n): ").strip().lower()
                if cont == 'y':
                    build_exe(console_mode=True)
            else:
                print_error("Сначала установите зависимости (опция 1)")
            
            input("\nНажмите Enter для продолжения...")
            
        elif choice == '4':
            # Очистка
            clean_build_files()
            input("\nНажмите Enter для продолжения...")
            
        elif choice == '5':
            # Тестирование
            run_full_test()
            input("\nНажмите Enter для продолжения...")
            
        elif choice == '6':
            # Выход
            print_header("Выход")
            print_success("До свидания!")
            print()
            break
            
        else:
            print_error("Неверный выбор. Введите число от 1 до 6.")
            input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Программа прервана{Colors.RESET}")
        sys.exit(0)
    except EOFError:
        # Обработка ситуации когда stdin закрыт (автоматические тесты)
        print(f"\n\n{Colors.YELLOW}Ввод завершен досрочно{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Критическая ошибка: {str(e)}{Colors.RESET}")
        print("Терминал останется открытым для просмотра ошибки")
        import traceback
        traceback.print_exc()
        try:
            input("Нажмите Enter для выхода...")
        except EOFError:
            pass
        sys.exit(1)
