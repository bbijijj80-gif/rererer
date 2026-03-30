#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor GUI - Графический интерфейс мониторинга системы
Использует tkinter для отображения показателей в реальном времени
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from core import SystemMonitorCore, SystemSnapshot


class SystemMonitorGUI:
    """Графический интерфейс для мониторинга системы"""

    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ System Monitor - Мониторинг системы")
        self.root.geometry("1200x800")
        
        # Создаем ядро мониторинга
        self.core = SystemMonitorCore()
        self.current_snapshot = None
        self.monitoring_active = False
        
        # Настройка стиля
        self.setup_styles()
        
        # Создание интерфейса
        self.create_menu()
        self.create_main_interface()
        
        # Обработчик закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цвета
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'info': '#2196F3',
            'card_bg': '#2d2d2d',
            'header_bg': '#3d3d3d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'], font=('Segoe UI', 10))
        style.configure('Header.TLabel', background=self.colors['header_bg'], foreground=self.colors['fg'], font=('Segoe UI', 12, 'bold'))
        style.configure('Card.TFrame', background=self.colors['card_bg'])
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='white')
        style.configure('Danger.TButton', background=self.colors['danger'], foreground='white')

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить отчет", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        # Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Обновить сейчас", command=self.update_display)
        
        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def create_main_interface(self):
        """Создание основного интерфейса"""
        # Верхняя панель с кнопками
        top_frame = tk.Frame(self.root, bg=self.colors['header_bg'], height=60)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.title_label = tk.Label(
            top_frame, 
            text="🖥️ System Monitor", 
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['header_bg'],
            fg=self.colors['fg']
        )
        self.title_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(
            top_frame,
            text="● Остановлено",
            font=('Segoe UI', 10),
            bg=self.colors['header_bg'],
            fg=self.colors['danger']
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Кнопки управления
        self.start_btn = tk.Button(
            top_frame,
            text="▶ Запустить мониторинг",
            command=self.toggle_monitoring,
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        self.start_btn.pack(side=tk.RIGHT, padx=10)
        
        # Основной контейнер с прокруткой
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas для прокрутки
        canvas = tk.Canvas(main_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Привязка колесика мыши
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Создание карточек с метриками
        self.create_metric_cards()

    def create_metric_cards(self):
        """Создание карточек с метриками"""
        # Сетка для карточек
        cards_frame = self.scrollable_frame
        
        # Row 0: CPU и Memory
        cpu_frame = self.create_card(cards_frame, "🔹 CPU", 0, 0)
        self.cpu_widgets = self.create_progress_card(cpu_frame, ["Загрузка:", "Частота:", "Ядра:", "Load Avg:"])
        
        mem_frame = self.create_card(cards_frame, "💾 Память", 0, 1)
        self.mem_widgets = self.create_progress_card(mem_frame, ["Всего:", "Использовано:", "Доступно:", "Swap:"])
        
        # Row 1: Disk и Network
        disk_frame = self.create_card(cards_frame, "💿 Диск", 1, 0)
        self.disk_widgets = self.create_info_card(disk_frame, 5)
        
        net_frame = self.create_card(cards_frame, "🌐 Сеть", 1, 1)
        self.net_widgets = self.create_info_card(net_frame, 5)
        
        # Row 2: Processes и GPU
        proc_frame = self.create_card(cards_frame, "⚙️ Процессы", 2, 0)
        self.proc_widgets = self.create_info_card(proc_frame, 5)
        
        gpu_frame = self.create_card(cards_frame, "🎮 GPU", 2, 1)
        self.gpu_widgets = self.create_info_card(gpu_frame, 5)
        
        # Row 3: System Info
        sys_frame = self.create_card(cards_frame, "ℹ️ Системная информация", 3, 0, colspan=2)
        self.sys_widgets = self.create_info_card(sys_frame, 6)
        
        # Row 4: Температура и Батарея
        temp_frame = self.create_card(cards_frame, "🌡️ Температура", 4, 0)
        self.temp_widgets = self.create_info_card(temp_frame, 5)
        
        batt_frame = self.create_card(cards_frame, "🔋 Батарея", 4, 1)
        self.batt_widgets = self.create_info_card(batt_frame, 4)
        
        # Row 5: Лог событий
        log_frame = self.create_card(cards_frame, "📋 Лог событий", 5, 0, colspan=2)
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Consolas', 9),
            height=8,
            relief=tk.FLAT
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_card(self, parent, title, row, col, rowspan=1, colspan=1):
        """Создание карточки"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, borderwidth=1)
        card.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=5, pady=5, ipadx=10, ipady=10)
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Заголовок
        header = tk.Label(
            card,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['header_bg'],
            fg=self.colors['fg'],
            pady=5
        )
        header.pack(fill=tk.X, padx=0, pady=0)
        
        # Контент
        content = tk.Frame(card, bg=self.colors['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        return content

    def create_progress_card(self, parent, labels):
        """Создание карточки с прогресс-барами"""
        widgets = {}
        for label_text in labels:
            frame = tk.Frame(parent, bg=self.colors['card_bg'])
            frame.pack(fill=tk.X, pady=3)
            
            label = tk.Label(
                frame,
                text=label_text,
                font=('Segoe UI', 10),
                bg=self.colors['card_bg'],
                fg=self.colors['fg'],
                width=15,
                anchor='w'
            )
            label.pack(side=tk.LEFT)
            
            progress = ttk.Progressbar(frame, length=200, mode='determinate')
            progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            value = tk.Label(
                frame,
                text="0%",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['card_bg'],
                fg=self.colors['accent'],
                width=8
            )
            value.pack(side=tk.RIGHT)
            
            widgets[label_text] = {'progress': progress, 'value': value}
        
        return widgets

    def create_info_card(self, parent, num_rows):
        """Создание информационной карточки"""
        widgets = []
        for i in range(num_rows):
            frame = tk.Frame(parent, bg=self.colors['card_bg'])
            frame.pack(fill=tk.X, pady=2)
            
            label = tk.Label(
                frame,
                text=f"Info {i+1}:",
                font=('Segoe UI', 9),
                bg=self.colors['card_bg'],
                fg=self.colors['fg'],
                anchor='w'
            )
            label.pack(side=tk.LEFT)
            
            value = tk.Label(
                frame,
                text="-",
                font=('Segoe UI', 9),
                bg=self.colors['card_bg'],
                fg=self.colors['info'],
                anchor='w'
            )
            value.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            
            widgets.append({'label': label, 'value': value})
        
        return widgets

    def toggle_monitoring(self):
        """Переключение режима мониторинга"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_btn.config(text="⏸ Остановить мониторинг", bg=self.colors['danger'])
            self.status_label.config(text="● Активно", fg=self.colors['accent'])
            self.log_event("Мониторинг запущен")
            
            # Запускаем поток обновления
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.monitoring_active = False
            self.start_btn.config(text="▶ Запустить мониторинг", bg=self.colors['accent'])
            self.status_label.config(text="● Остановлено", fg=self.colors['danger'])
            self.log_event("Мониторинг остановлен")

    def monitor_loop(self):
        """Цикл мониторинга"""
        while self.monitoring_active:
            try:
                self.current_snapshot = self.core.get_snapshot()
                self.root.after(0, self.update_display)
                time.sleep(1.0)
            except Exception as e:
                self.root.after(0, lambda: self.log_event(f"Ошибка: {str(e)}"))
                time.sleep(1.0)

    def update_display(self):
        """Обновление отображаемых данных"""
        if not self.current_snapshot:
            return
        
        snapshot = self.current_snapshot
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            # CPU
            if "Загрузка:" in self.cpu_widgets:
                self.cpu_widgets["Загрузка:"]['progress'].config(value=snapshot.cpu.usage_percent)
                self.cpu_widgets["Загрузка:"]['value'].config(text=f"{snapshot.cpu.usage_percent:.1f}%")
                
                freq_mhz = snapshot.cpu.freq_current / 1000 if snapshot.cpu.freq_current > 1000 else snapshot.cpu.freq_current
                self.cpu_widgets["Частота:"]['value'].config(text=f"{freq_mhz:.2f} ГГц")
                self.cpu_widgets["Частота:"]['progress'].config(value=(snapshot.cpu.freq_current / snapshot.cpu.freq_max * 100) if snapshot.cpu.freq_max > 0 else 0)
                
                self.cpu_widgets["Ядра:"]['value'].config(text=f"{snapshot.cpu.cores_physical}P + {snapshot.cpu.cores_logical - snapshot.cpu.cores_physical}E")
                
                if snapshot.cpu.load_avg_1 > 0:
                    load_text = f"{snapshot.cpu.load_avg_1:.2f} | {snapshot.cpu.load_avg_5:.2f} | {snapshot.cpu.load_avg_15:.2f}"
                    self.cpu_widgets["Load Avg:"]['value'].config(text=load_text)
            
            # Memory
            if len(self.mem_widgets) >= 4:
                total_gb = snapshot.memory.total / (1024**3)
                used_gb = snapshot.memory.used / (1024**3)
                avail_gb = snapshot.memory.available / (1024**3)
                
                self.mem_widgets[0]['label'].config(text="Всего:")
                self.mem_widgets[0]['value'].config(text=f"{total_gb:.2f} GB")
                
                self.mem_widgets[1]['label'].config(text="Использовано:")
                self.mem_widgets[1]['value'].config(text=f"{used_gb:.2f} GB ({snapshot.memory.percent:.1f}%)")
                self.mem_widgets[1]['value'].config(fg=self.get_color_for_percent(snapshot.memory.percent))
                
                self.mem_widgets[2]['label'].config(text="Доступно:")
                self.mem_widgets[2]['value'].config(text=f"{avail_gb:.2f} GB")
                
                if snapshot.memory.swap_total > 0:
                    swap_percent = snapshot.memory.swap_percent
                    self.mem_widgets[3]['label'].config(text="Swap:")
                    self.mem_widgets[3]['value'].config(text=f"{swap_percent:.1f}%")
            
            # Disk
            if snapshot.disk.partitions:
                for i, part in enumerate(snapshot.disk.partitions[:4]):
                    if i < len(self.disk_widgets):
                        mount = part['mountpoint']
                        used_gb = part['used'] / (1024**3)
                        total_gb = part['total'] / (1024**3)
                        self.disk_widgets[i]['label'].config(text=f"{mount}:")
                        self.disk_widgets[i]['value'].config(text=f"{used_gb:.1f}/{total_gb:.1f} GB ({part['percent']})")
            
            # Network
            if len(self.net_widgets) >= 4:
                sent_mb = snapshot.network.bytes_sent / (1024**2)
                recv_mb = snapshot.network.bytes_recv / (1024**2)
                
                self.net_widgets[0]['label'].config(text="Отправлено:")
                self.net_widgets[0]['value'].config(text=f"{sent_mb:.2f} MB")
                
                self.net_widgets[1]['label'].config(text="Получено:")
                self.net_widgets[1]['value'].config(text=f"{recv_mb:.2f} MB")
                
                self.net_widgets[2]['label'].config(text="IP адрес:")
                self.net_widgets[2]['value'].config(text=snapshot.network.ip_address)
                
                self.net_widgets[3]['label'].config(text="Подключений:")
                self.net_widgets[3]['value'].config(text=str(len(snapshot.network.connections)))
            
            # Processes
            if len(self.proc_widgets) >= 4:
                self.proc_widgets[0]['label'].config(text="Всего процессов:")
                self.proc_widgets[0]['value'].config(text=str(snapshot.processes.total_processes))
                
                self.proc_widgets[1]['label'].config(text="Активных:")
                self.proc_widgets[1]['value'].config(text=str(snapshot.processes.running_processes))
                
                if snapshot.processes.top_cpu_processes:
                    top_proc = snapshot.processes.top_cpu_processes[0]
                    self.proc_widgets[2]['label'].config(text="Top CPU:")
                    self.proc_widgets[2]['value'].config(text=f"{top_proc['name']} ({top_proc['cpu_percent']:.1f}%)")
                
                if snapshot.processes.top_memory_processes:
                    top_mem = snapshot.processes.top_memory_processes[0]
                    self.proc_widgets[3]['label'].config(text="Top RAM:")
                    self.proc_widgets[3]['value'].config(text=f"{top_mem['name']} ({top_mem['memory_percent']:.1f}%)")
            
            # GPU
            if snapshot.gpu.available:
                self.gpu_widgets[0]['label'].config(text="GPU:")
                self.gpu_widgets[0]['value'].config(text=snapshot.gpu.gpu_name[:40])
                
                self.gpu_widgets[1]['label'].config(text="Загрузка:")
                self.gpu_widgets[1]['value'].config(text=f"{snapshot.gpu.gpu_load}%")
                
                mem_used_mb = snapshot.gpu.gpu_memory_used / (1024**2)
                mem_total_mb = snapshot.gpu.gpu_memory_total / (1024**2)
                self.gpu_widgets[2]['label'].config(text="Память:")
                self.gpu_widgets[2]['value'].config(text=f"{mem_used_mb:.0f}/{mem_total_mb:.0f} MB")
            else:
                self.gpu_widgets[0]['label'].config(text="GPU:")
                self.gpu_widgets[0]['value'].config(text="Не обнаружено")
            
            # System
            if len(self.sys_widgets) >= 5:
                self.sys_widgets[0]['label'].config(text="ОС:")
                self.sys_widgets[0]['value'].config(text=f"{snapshot.system.system} {snapshot.system.release}")
                
                self.sys_widgets[1]['label'].config(text="Хост:")
                self.sys_widgets[1]['value'].config(text=snapshot.system.node)
                
                uptime_hours = snapshot.system.uptime_seconds / 3600
                self.sys_widgets[2]['label'].config(text="Время работы:")
                self.sys_widgets[2]['value'].config(text=f"{uptime_hours:.2f} часов")
                
                self.sys_widgets[3]['label'].config(text="Процессор:")
                self.sys_widgets[3]['value'].config(text=snapshot.system.processor[:50])
                
                self.sys_widgets[4]['label'].config(text="Python:")
                self.sys_widgets[4]['value'].config(text=snapshot.system.python_version)
            
            # Temperature
            if snapshot.temperature.available and snapshot.temperature.sensors:
                sensor_count = 0
                for sensor_name, sensors in snapshot.temperature.sensors.items():
                    for sensor in sensors[:2]:
                        if sensor_count < len(self.temp_widgets):
                            self.temp_widgets[sensor_count]['label'].config(text=f"{sensor_name}:")
                            self.temp_widgets[sensor_count]['value'].config(text=f"{sensor['label']}: {sensor['current']}°C")
                            sensor_count += 1
            else:
                self.temp_widgets[0]['label'].config(text="Температура:")
                self.temp_widgets[0]['value'].config(text="Данные недоступны")
            
            # Battery
            if snapshot.battery.available:
                self.batt_widgets[0]['label'].config(text="Заряд:")
                self.batt_widgets[0]['value'].config(text=f"{snapshot.battery.percent}%")
                color = self.get_color_for_percent(snapshot.battery.percent)
                self.batt_widgets[0]['value'].config(fg=color)
                
                self.batt_widgets[1]['label'].config(text="Питание:")
                status = "Подключено" if snapshot.battery.plugged_in else "От батареи"
                self.batt_widgets[1]['value'].config(text=status)
                
                self.batt_widgets[2]['label'].config(text="Осталось:")
                self.batt_widgets[2]['value'].config(text=snapshot.battery.time_left)
            else:
                self.batt_widgets[0]['label'].config(text="Батарея:")
                self.batt_widgets[0]['value'].config(text="Не обнаружена")
            
            # Обновляем заголовок с временем
            self.title_label.config(text=f"🖥️ System Monitor - {timestamp}")
            
        except Exception as e:
            self.log_event(f"Ошибка обновления: {str(e)}")

    def get_color_for_percent(self, percent):
        """Получить цвет в зависимости от процента"""
        if percent < 50:
            return self.colors['accent']
        elif percent < 80:
            return self.colors['warning']
        else:
            return self.colors['danger']

    def log_event(self, message):
        """Логирование события"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def save_report(self):
        """Сохранение отчета"""
        if not self.current_snapshot:
            messagebox.showinfo("Информация", "Сначала запустите мониторинг")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.core.to_json(self.current_snapshot))
                messagebox.showinfo("Успех", f"Отчет сохранен в {filename}")
                self.log_event(f"Отчет сохранен: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}")

    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo(
            "О программе",
            "🖥️ System Monitor v1.0\n\n"
            "Программа для мониторинга системных показателей в реальном времени.\n\n"
            "Функции:\n"
            "• Мониторинг CPU, RAM, Disk, Network\n"
            "• Информация о процессах\n"
            "• Данные GPU (если доступно)\n"
            "• Температура и батарея\n\n"
            "© 2024 System Monitor"
        )

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.monitoring_active:
            self.monitoring_active = False
            time.sleep(0.5)
        
        self.root.destroy()


def main():
    """Точка входа"""
    root = tk.Tk()
    app = SystemMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
