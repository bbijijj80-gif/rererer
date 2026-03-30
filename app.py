"""
System Monitor Application
Графическое приложение для мониторинга системы с использованием реального ядра
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from core import SystemCore


class SystemMonitorApp:
    """Графическое приложение для мониторинга системы"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor - Реальное Ядро")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Инициализация ядра
        self.core = SystemCore()
        self.current_data = None
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск обновления данных
        self.update_data()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Настройка стилей приложения"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Конфигурация стилей
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Value.TLabel', font=('Arial', 11))
        style.configure('Status.TLabel', font=('Arial', 10))
        
        # Цвета для прогресс-баров
        style.configure('CPU.Horizontal.TProgressbar', troughcolor='#d9d9d9', background='#4CAF50')
        style.configure('Memory.Horizontal.TProgressbar', troughcolor='#d9d9d9', background='#2196F3')
        style.configure('Disk.Horizontal.TProgressbar', troughcolor='#d9d9d9', background='#FF9800')
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер с прокруткой
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas для прокрутки
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Привязка колесика мыши
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        title_label = ttk.Label(scrollable_frame, text="🖥️ System Monitor", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Фрейм для системной информации
        self.create_system_info_frame(scrollable_frame)
        
        # Фрейм для CPU
        self.create_cpu_frame(scrollable_frame)
        
        # Фрейм для памяти
        self.create_memory_frame(scrollable_frame)
        
        # Фрейм для дисков
        self.create_disk_frame(scrollable_frame)
        
        # Фрейм для сети
        self.create_network_frame(scrollable_frame)
        
        # Фрейм для процессов
        self.create_processes_frame(scrollable_frame)
        
        # Кнопки управления
        self.create_control_buttons(scrollable_frame)
    
    def create_system_info_frame(self, parent):
        """Создание фрейма с системной информацией"""
        frame = ttk.LabelFrame(parent, text="Системная информация", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.system_info_label = ttk.Label(frame, text="Загрузка...", style='Value.TLabel')
        self.system_info_label.pack(anchor=tk.W)
    
    def create_cpu_frame(self, parent):
        """Создание фрейма с информацией о CPU"""
        frame = ttk.LabelFrame(parent, text="Процессор (CPU)", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Общий процент использования
        cpu_header = ttk.Frame(frame)
        cpu_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cpu_header, text="Использование:", style='Header.TLabel').pack(side=tk.LEFT)
        self.cpu_percent_label = ttk.Label(cpu_header, text="0%", style='Value.TLabel')
        self.cpu_percent_label.pack(side=tk.RIGHT)
        
        # Прогресс-бар
        self.cpu_progress = ttk.Progressbar(frame, style='CPU.Horizontal.TProgressbar', length=400)
        self.cpu_progress.pack(fill=tk.X, pady=5)
        
        # Детали
        details_frame = ttk.Frame(frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        self.cpu_details_label = ttk.Label(details_frame, text="", style='Value.TLabel')
        self.cpu_details_label.pack(anchor=tk.W)
        
        # Использование по ядрам
        self.cpu_cores_frame = ttk.Frame(frame)
        self.cpu_cores_frame.pack(fill=tk.X, pady=5)
        self.cpu_core_bars = []
    
    def create_memory_frame(self, parent):
        """Создание фрейма с информацией о памяти"""
        frame = ttk.LabelFrame(parent, text="Оперативная память (RAM)", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Процент использования
        mem_header = ttk.Frame(frame)
        mem_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mem_header, text="Использование:", style='Header.TLabel').pack(side=tk.LEFT)
        self.mem_percent_label = ttk.Label(mem_header, text="0%", style='Value.TLabel')
        self.mem_percent_label.pack(side=tk.RIGHT)
        
        # Прогресс-бар
        self.mem_progress = ttk.Progressbar(frame, style='Memory.Horizontal.TProgressbar', length=400)
        self.mem_progress.pack(fill=tk.X, pady=5)
        
        # Детали
        self.mem_details_label = ttk.Label(frame, text="", style='Value.TLabel')
        self.mem_details_label.pack(anchor=tk.W, pady=10)
    
    def create_disk_frame(self, parent):
        """Создание фрейма с информацией о дисках"""
        frame = ttk.LabelFrame(parent, text="Диски", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.disk_list_frame = ttk.Frame(frame)
        self.disk_list_frame.pack(fill=tk.X)
        
        self.disk_widgets = []
    
    def create_network_frame(self, parent):
        """Создание фрейма с информацией о сети"""
        frame = ttk.LabelFrame(parent, text="Сеть", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.network_label = ttk.Label(frame, text="", style='Value.TLabel')
        self.network_label.pack(anchor=tk.W)
    
    def create_processes_frame(self, parent):
        """Создание фрейма со списком процессов"""
        frame = ttk.LabelFrame(parent, text="Топ процессов (по памяти)", padding="15")
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Таблица процессов
        columns = ('name', 'pid', 'memory', 'cpu')
        self.process_tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        
        self.process_tree.heading('name', text='Процесс')
        self.process_tree.heading('pid', text='PID')
        self.process_tree.heading('memory', text='Память %')
        self.process_tree.heading('cpu', text='CPU %')
        
        self.process_tree.column('name', width=300)
        self.process_tree.column('pid', width=80)
        self.process_tree.column('memory', width=100)
        self.process_tree.column('cpu', width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_control_buttons(self, parent):
        """Создание кнопок управления"""
        frame = ttk.Frame(parent)
        frame.pack(pady=20)
        
        self.start_button = ttk.Button(frame, text="▶ Запустить мониторинг", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(frame, text="⏸ Остановить", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(frame, text="🔄 Обновить", command=self.update_data)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(frame, text="Готов", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=20)
    
    def update_data(self):
        """Обновление данных интерфейса"""
        try:
            data = self.core.get_all_data()
            self.current_data = data
            
            # Системная информация
            sys_info = data['system']
            system_text = (
                f"OS: {sys_info['system']} {sys_info['release']}\n"
                f"Host: {sys_info['node']}\n"
                f"Python: {sys_info['python_version']}\n"
                f"Время работы: {sys_info['uptime']}\n"
                f"Загрузка: {sys_info['boot_time']}"
            )
            self.system_info_label.config(text=system_text)
            
            # CPU
            cpu = data['cpu']
            cpu_usage = cpu['usage_percent']
            self.cpu_percent_label.config(text=f"{cpu_usage:.1f}%")
            self.cpu_progress['value'] = cpu_usage
            
            # Цвет прогресс-бара в зависимости от нагрузки
            if cpu_usage < 50:
                color = '#4CAF50'  # Зеленый
            elif cpu_usage < 80:
                color = '#FFC107'  # Желтый
            else:
                color = '#F44336'  # Красный
            
            style = ttk.Style()
            style.configure('CPU.Horizontal.TProgressbar', background=color)
            
            cpu_details = (
                f"Частота: {cpu['frequency_current']:.0f} MHz / {cpu['frequency_max']:.0f} MHz\n"
                f"Ядра: {cpu['cores_physical']} физических, {cpu['cores_logical']} логических"
            )
            self.cpu_details_label.config(text=cpu_details)
            
            # Ядра
            for widget in self.cpu_cores_frame.winfo_children():
                widget.destroy()
            
            per_cpu = cpu['per_cpu_usage']
            for i, usage in enumerate(per_cpu[:8]):  # Показываем максимум 8 ядер
                core_frame = ttk.Frame(self.cpu_cores_frame)
                core_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(core_frame, text=f"Ядро {i+1}:").pack(side=tk.LEFT, padx=5)
                progress = ttk.Progressbar(core_frame, length=200, mode='determinate')
                progress['value'] = usage
                progress.pack(side=tk.LEFT, padx=5)
                ttk.Label(core_frame, text=f"{usage:.1f}%").pack(side=tk.LEFT)
            
            # Память
            mem = data['memory']
            mem_usage = mem['percent']
            self.mem_percent_label.config(text=f"{mem_usage:.1f}%")
            self.mem_progress['value'] = mem_usage
            
            # Цвет прогресс-бара памяти
            if mem_usage < 50:
                color = '#2196F3'  # Синий
            elif mem_usage < 80:
                color = '#FFC107'  # Желтый
            else:
                color = '#F44336'  # Красный
            
            style.configure('Memory.Horizontal.TProgressbar', background=color)
            
            mem_details = (
                f"Всего: {self.core.format_bytes(mem['total'])}\n"
                f"Использовано: {self.core.format_bytes(mem['used'])}\n"
                f"Доступно: {self.core.format_bytes(mem['available'])}\n"
                f"Swap: {self.core.format_bytes(mem['swap_used'])} / {self.core.format_bytes(mem['swap_total'])} ({mem['swap_percent']:.1f}%)"
            )
            self.mem_details_label.config(text=mem_details)
            
            # Диски
            for widget in self.disk_list_frame.winfo_children():
                widget.destroy()
            
            for disk in data['disk']:
                disk_frame = ttk.LabelFrame(self.disk_list_frame, text=f"{disk['mountpoint']} ({disk['device']})", padding="10")
                disk_frame.pack(fill=tk.X, pady=5)
                
                header = ttk.Frame(disk_frame)
                header.pack(fill=tk.X, pady=(0, 5))
                
                ttk.Label(header, text=f"{disk['fstype']} | Использовано:").pack(side=tk.LEFT)
                percent_label = ttk.Label(header, text=f"{disk['percent']:.1f}%")
                percent_label.pack(side=tk.RIGHT)
                
                progress = ttk.Progressbar(disk_frame, style='Disk.Horizontal.TProgressbar', length=400)
                progress['value'] = disk['percent']
                progress.pack(fill=tk.X, pady=5)
                
                details = f"{self.core.format_bytes(disk['used'])} / {self.core.format_bytes(disk['total'])} (Свободно: {self.core.format_bytes(disk['free'])})"
                ttk.Label(disk_frame, text=details).pack(anchor=tk.W)
            
            # Сеть
            net = data['network']
            network_text = (
                f"Отправлено: {self.core.format_bytes(net['bytes_sent'])}\n"
                f"Получено: {self.core.format_bytes(net['bytes_recv'])}\n"
                f"Пакеты отправлено: {net['packets_sent']:,}\n"
                f"Пакеты получено: {net['packets_recv']:,}\n"
                f"Интерфейсы: {', '.join(net['interfaces'].keys())}"
            )
            self.network_label.config(text=network_text)
            
            # Процессы
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            for proc in data['top_processes']:
                self.process_tree.insert('', tk.END, values=(
                    proc['name'],
                    proc['pid'],
                    f"{proc['memory_percent']:.1f}%",
                    f"{proc['cpu_percent']:.1f}%"
                ))
            
            self.status_label.config(text=f"Обновлено: {data['timestamp']}")
            
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось обновить данные:\n{str(e)}")
    
    def start_monitoring(self):
        """Запуск автоматического мониторинга"""
        self.core.start(interval=1.0)
        self.core.register_callback(self.on_core_update)
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Мониторинг запущен")
    
    def stop_monitoring(self):
        """Остановка автоматического мониторинга"""
        self.core.stop()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Мониторинг остановлен")
    
    def on_core_update(self, data):
        """Обработчик обновлений от ядра"""
        # Обновляем интерфейс в главном потоке
        self.root.after(0, lambda: self.update_data_from_core(data))
    
    def update_data_from_core(self, data):
        """Обновление данных из ядра"""
        self.current_data = data
        # Вызываем обновление интерфейса
        self.update_data()
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.core.stop()
        self.root.destroy()


def main():
    """Точка входа приложения"""
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
