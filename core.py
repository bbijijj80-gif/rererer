"""
Real System Monitor Core
Это настоящее ядро системы мониторинга, которое получает реальные данные о системе
"""

import psutil
import platform
import socket
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time


class SystemCore:
    """Реальное ядро для мониторинга системы"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 1.0  # секунды
        self.callbacks = []
        self._thread = None
        self._data_cache = {}
        
    def register_callback(self, callback):
        """Регистрация обратного вызова для обновления данных"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Удаление обратного вызова"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, data: Dict):
        """Уведомление всех зарегистрированных обработчиков"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def get_cpu_info(self) -> Dict:
        """Получение информации о процессоре"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        
        return {
            'usage_percent': cpu_percent,
            'frequency_current': cpu_freq.current if cpu_freq else 0,
            'frequency_max': cpu_freq.max if cpu_freq else 0,
            'cores_logical': cpu_count,
            'cores_physical': cpu_count_physical,
            'per_cpu_usage': per_cpu
        }
    
    def get_memory_info(self) -> Dict:
        """Получение информации об оперативной памяти"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self) -> List[Dict]:
        """Получение информации о дисках"""
        disks = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except PermissionError:
                continue
        
        return disks
    
    def get_network_info(self) -> Dict:
        """Получение информации о сети"""
        net_io = psutil.net_io_counters()
        net_if_addrs = psutil.net_if_addrs()
        
        interfaces = {}
        for iface, addrs in net_if_addrs.items():
            interfaces[iface] = {
                'addresses': [str(addr.address) for addr in addrs if addr.family == socket.AF_INET]
            }
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'interfaces': interfaces
        }
    
    def get_process_list(self, limit: int = 10) -> List[Dict]:
        """Получение списка процессов по потреблению памяти"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Сортировка по потреблению памяти
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        return processes[:limit]
    
    def get_system_info(self) -> Dict:
        """Получение общей информации о системе"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': str(datetime.now() - boot_time).split('.')[0]
        }
    
    def get_all_data(self) -> Dict:
        """Получение всех данных о системе"""
        data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'top_processes': self.get_process_list(5)
        }
        
        self._data_cache = data
        return data
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.running:
            try:
                data = self.get_all_data()
                self._notify_callbacks(data)
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def start(self, interval: float = 1.0):
        """Запуск мониторинга в отдельном потоке"""
        if self.running:
            return
        
        self.running = True
        self.update_interval = interval
        self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._thread.start()
        print("System core started")
    
    def stop(self):
        """Остановка мониторинга"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        print("System core stopped")
    
    def format_bytes(self, bytes_value: int) -> str:
        """Форматирование размера в байтах в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


# Экспорт основного экземпляра ядра
core = SystemCore()

if __name__ == "__main__":
    # Тестирование ядра
    print("Testing System Core...")
    print("=" * 50)
    
    test_core = SystemCore()
    data = test_core.get_all_data()
    
    print(f"System: {data['system']['system']} {data['system']['release']}")
    print(f"Python: {data['system']['python_version']}")
    print(f"Uptime: {data['system']['uptime']}")
    print(f"CPU Usage: {data['cpu']['usage_percent']}%")
    print(f"Memory Usage: {data['memory']['percent']}%")
    print(f"CPU Cores: {data['cpu']['cores_logical']} logical, {data['cpu']['cores_physical']} physical")
    
    print("\nDisk Usage:")
    for disk in data['disk']:
        print(f"  {disk['mountpoint']}: {test_core.format_bytes(disk['used'])} / {test_core.format_bytes(disk['total'])} ({disk['percent']}%)")
    
    print("\nTop Processes:")
    for proc in data['top_processes']:
        print(f"  {proc['name']}: {proc['memory_percent']:.1f}% RAM")
    
    print("=" * 50)
    print("Core test completed successfully!")
