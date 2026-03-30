#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor - Главное приложение
Запускает графический интерфейс мониторинга системы
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core import SystemMonitorCore
    from gui import SystemMonitorGUI
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что файлы core.py и gui.py находятся в той же директории")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)


def main():
    """Точка входа приложения"""
    print("=" * 60)
    print("🖥️  System Monitor - Запуск...")
    print("=" * 60)
    
    # Инициализация ядра
    try:
        core = SystemMonitorCore()
        print("✅ Ядро мониторинга инициализировано")
        
        # Быстрая проверка работоспособности
        snapshot = core.get_snapshot()
        # snapshot - это dataclass, доступ через атрибуты
        print(f"   CPU: {snapshot.cpu.usage_percent:.1f}%")
        print(f"   RAM: {snapshot.memory.percent:.1f}%")
        print(f"   Система: {snapshot.system.system}")
    except Exception as e:
        print(f"❌ Ошибка инициализации ядра: {e}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
    
    print("\n🚀 Запуск графического интерфейса...")
    print("-" * 60)
    
    # Запуск GUI
    try:
        app = SystemMonitorGUI(core)
        app.run()
    except Exception as e:
        print(f"\n❌ Ошибка запуска GUI: {e}")
        print("\nВозможные причины:")
        print("  - Не установлен tkinter (попробуйте: pip install tk)")
        print("  - Проблемы с графической подсистемой")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    main()
