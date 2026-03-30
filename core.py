#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor Core - Реальное ядро мониторинга системы
Собирает показатели CPU, RAM, Disk, Network, GPU, Temperature и др.
"""

import psutil
import platform
import socket
import datetime
import json
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class MetricType(Enum):
    """Типы метрик"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    TEMPERATURE = "temperature"
    PROCESSES = "processes"
    SYSTEM = "system"
    BATTERY = "battery"


@dataclass
class CPUMetrics:
    """Метрики процессора"""
    usage_percent: float
    cores_physical: int
    cores_logical: int
    freq_current: float
    freq_max: float
    per_core_usage: List[float]
    load_avg_1: float = 0.0
    load_avg_5: float = 0.0
    load_avg_15: float = 0.0
    context_switches: int = 0
    interrupts: int = 0


@dataclass
class MemoryMetrics:
    """Метрики оперативной памяти"""
    total: int
    available: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_free: int
    swap_percent: float


@dataclass
class DiskMetrics:
    """Метрики дисковой подсистемы"""
    partitions: List[Dict[str, Any]]
    io_read_bytes: int
    io_write_bytes: int
    io_read_count: int
    io_write_count: int
    io_time: float
    total_space: int
    used_space: int
    free_space: int
    percent_used: float


@dataclass
class NetworkMetrics:
    """Сетевые метрики"""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    connections: List[Dict[str, Any]]
    hostname: str
    ip_address: str


@dataclass
class ProcessMetrics:
    """Метрики процессов"""
    total_processes: int
    running_processes: int
    top_cpu_processes: List[Dict[str, Any]]
    top_memory_processes: List[Dict[str, Any]]


@dataclass
class SystemMetrics:
    """Общие системные метрики"""
    system: str
    node: str
    release: str
    version: str
    machine: str
    processor: str
    boot_time: str
    uptime_seconds: float
    python_version: str


@dataclass
class GPUMetrics:
    """Метрики GPU (если доступны)"""
    available: bool
    gpu_name: str = ""
    gpu_load: float = 0.0
    gpu_memory_total: int = 0
    gpu_memory_used: int = 0
    gpu_memory_percent: float = 0.0
    gpu_temperature: float = 0.0


@dataclass
class BatteryMetrics:
    """Метрики батареи (для ноутбуков)"""
    available: bool
    plugged_in: bool = False
    percent: float = 0.0
    secsleft: int = 0
    time_left: str = ""


@dataclass
class TemperatureMetrics:
    """Температурные метрики"""
    available: bool
    sensors: Dict[str, List[Dict[str, Any]]]


@dataclass
class SystemSnapshot:
    """Полный снимок состояния системы"""
    timestamp: str
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    processes: ProcessMetrics
    system: SystemMetrics
    gpu: GPUMetrics
    battery: BatteryMetrics
    temperature: TemperatureMetrics


class SystemMonitorCore:
    """
    Основное ядро мониторинга системы
    Собирает все доступные показатели в реальном времени
    """

    def __init__(self):
        self._running = False
        self._update_interval = 1.0  # секунды
        self._callbacks: List[callable] = []
        self._last_snapshot: Optional[SystemSnapshot] = None
        self._monitor_thread: Optional[threading.Thread] = None

    def add_callback(self, callback: callable):
        """Добавить коллбэк для уведомления об обновлениях"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: callable):
        """Удалить коллбэк"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _get_cpu_metrics(self) -> CPUMetrics:
        """Получить метрики CPU"""
        freq = psutil.cpu_freq()
        
        # Load average только для Unix-систем
        load_avg = getattr(psutil, 'getloadavg', lambda: (0, 0, 0))()
        
        return CPUMetrics(
            usage_percent=psutil.cpu_percent(interval=0),
            cores_physical=psutil.cpu_count(logical=False) or 1,
            cores_logical=psutil.cpu_count(logical=True) or 1,
            freq_current=freq.current if freq else 0.0,
            freq_max=freq.max if freq else 0.0,
            per_core_usage=psutil.cpu_percent(interval=0, percpu=True),
            load_avg_1=load_avg[0],
            load_avg_5=load_avg[1],
            load_avg_15=load_avg[2],
            context_switches=psutil.cpu_stats().ctx_switches,
            interrupts=psutil.cpu_stats().interrupts
        )

    def _get_memory_metrics(self) -> MemoryMetrics:
        """Получить метрики памяти"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return MemoryMetrics(
            total=mem.total,
            available=mem.available,
            used=mem.used,
            percent=mem.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            swap_percent=swap.percent
        )

    def _get_disk_metrics(self) -> DiskMetrics:
        """Получить метрики диска"""
        partitions_info = []
        total_space = 0
        used_space = 0
        free_space = 0
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
                # Суммируем только основные разделы
                if partition.device and not partition.device.startswith('/dev/loop'):
                    total_space += usage.total
                    used_space += usage.used
                    free_space += usage.free
            except PermissionError:
                continue
        
        io_counters = psutil.disk_io_counters()
        
        return DiskMetrics(
            partitions=partitions_info,
            io_read_bytes=io_counters.read_bytes if io_counters else 0,
            io_write_bytes=io_counters.write_bytes if io_counters else 0,
            io_read_count=io_counters.read_count if io_counters else 0,
            io_write_count=io_counters.write_count if io_counters else 0,
            io_time=io_counters.busy_time if io_counters else 0,
            total_space=total_space,
            used_space=used_space,
            free_space=free_space,
            percent_used=(used_space / total_space * 100) if total_space > 0 else 0
        )

    def _get_network_metrics(self) -> NetworkMetrics:
        """Получить сетевые метрики"""
        net_io = psutil.net_io_counters()
        
        connections_info = []
        for conn in psutil.net_connections(kind='inet')[:20]:  # Ограничим 20 соединениями
            connections_info.append({
                'family': 'IPv4' if conn.family == socket.AF_INET else 'IPv6',
                'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                'status': conn.status
            })
        
        # Получаем локальный IP
        ip_address = "unknown"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except Exception:
            pass
        
        return NetworkMetrics(
            bytes_sent=net_io.bytes_sent,
            bytes_recv=net_io.bytes_recv,
            packets_sent=net_io.packets_sent,
            packets_recv=net_io.packets_recv,
            errin=net_io.errin,
            errout=net_io.errout,
            dropin=net_io.dropin,
            dropout=net_io.dropout,
            connections=connections_info,
            hostname=socket.gethostname(),
            ip_address=ip_address
        )

    def _get_process_metrics(self) -> ProcessMetrics:
        """Получить метрики процессов"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'] or 'unknown',
                    'cpu_percent': info['cpu_percent'] or 0,
                    'memory_percent': info['memory_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Сортируем по CPU и памяти
        top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
        top_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
        
        running = sum(1 for p in processes if p['cpu_percent'] > 0)
        
        return ProcessMetrics(
            total_processes=len(processes),
            running_processes=running,
            top_cpu_processes=top_cpu,
            top_memory_processes=top_memory
        )

    def _get_system_metrics(self) -> SystemMetrics:
        """Получить общие системные метрики"""
        uname = platform.uname()
        boot_time = psutil.boot_time()
        uptime = datetime.datetime.now().timestamp() - boot_time
        
        return SystemMetrics(
            system=uname.system,
            node=uname.node,
            release=uname.release,
            version=uname.version,
            machine=uname.machine,
            processor=uname.processor or "unknown",
            boot_time=datetime.datetime.fromtimestamp(boot_time).isoformat(),
            uptime_seconds=uptime,
            python_version=platform.python_version()
        )

    def _get_gpu_metrics(self) -> GPUMetrics:
        """Получить метрики GPU"""
        gpu_metrics = GPUMetrics(available=False)
        
        # Попытка получить информацию через py3nvml (NVIDIA)
        try:
            from py3nvml import py3nvml
            py3nvml.nvmlInit()
            handle = py3nvml.nvmlDeviceGetHandleByIndex(0)
            
            gpu_metrics.available = True
            gpu_metrics.gpu_name = py3nvml.nvmlDeviceGetName(handle).decode('utf-8')
            gpu_metrics.gpu_load = py3nvml.nvmlDeviceGetUtilizationRates(handle).gpu
            mem_info = py3nvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_metrics.gpu_memory_total = mem_info.total
            gpu_metrics.gpu_memory_used = mem_info.used
            gpu_metrics.gpu_memory_percent = (mem_info.used / mem_info.total) * 100
            
            try:
                gpu_metrics.gpu_temperature = py3nvml.nvmlDeviceGetTemperature(handle, 0)
            except:
                pass
            
            py3nvml.nvmlShutdown()
        except ImportError:
            pass
        except Exception:
            pass
        
        # Попытка через pynvml (альтернативная библиотека)
        if not gpu_metrics.available:
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                gpu_metrics.available = True
                gpu_metrics.gpu_name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                gpu_metrics.gpu_load = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_metrics.gpu_memory_total = mem_info.total
                gpu_metrics.gpu_memory_used = mem_info.used
                gpu_metrics.gpu_memory_percent = (mem_info.used / mem_info.total) * 100
                
                pynvml.nvmlShutdown()
            except ImportError:
                pass
            except Exception:
                pass
        
        return gpu_metrics

    def _get_battery_metrics(self) -> BatteryMetrics:
        """Получить метрики батареи"""
        try:
            battery = psutil.sensors_battery()
        except Exception:
            # На некоторых системах (серверы, контейнеры) нет доступа к батарее
            return BatteryMetrics(available=False)
        
        if battery is None:
            return BatteryMetrics(available=False)
        
        time_left = "unknown"
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            time_left = f"{hours}h {minutes}m"
        
        return BatteryMetrics(
            available=True,
            plugged_in=battery.power_plugged,
            percent=battery.percent,
            secsleft=battery.secsleft,
            time_left=time_left
        )

    def _get_temperature_metrics(self) -> TemperatureMetrics:
        """Получить температурные метрики"""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return TemperatureMetrics(available=False, sensors={})
            
            sensors_data = {}
            for name, entries in temps.items():
                sensors_data[name] = [
                    {
                        'label': entry.label or f"Sensor {i}",
                        'current': entry.current,
                        'high': entry.high,
                        'critical': entry.critical
                    }
                    for i, entry in enumerate(entries)
                ]
            
            return TemperatureMetrics(available=True, sensors=sensors_data)
        except Exception:
            return TemperatureMetrics(available=False, sensors={})

    def get_snapshot(self) -> SystemSnapshot:
        """Получить полный снимок состояния системы"""
        snapshot = SystemSnapshot(
            timestamp=datetime.datetime.now().isoformat(),
            cpu=self._get_cpu_metrics(),
            memory=self._get_memory_metrics(),
            disk=self._get_disk_metrics(),
            network=self._get_network_metrics(),
            processes=self._get_process_metrics(),
            system=self._get_system_metrics(),
            gpu=self._get_gpu_metrics(),
            battery=self._get_battery_metrics(),
            temperature=self._get_temperature_metrics()
        )
        
        self._last_snapshot = snapshot
        return snapshot

    def to_dict(self, snapshot: Optional[SystemSnapshot] = None) -> Dict[str, Any]:
        """Преобразовать снимок в словарь"""
        if snapshot is None:
            snapshot = self._last_snapshot or self.get_snapshot()
        
        def convert(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            else:
                return obj
        
        return convert(asdict(snapshot))

    def to_json(self, snapshot: Optional[SystemSnapshot] = None, indent: int = 2) -> str:
        """Преобразовать снимок в JSON"""
        return json.dumps(self.to_dict(snapshot), indent=indent, ensure_ascii=False)

    def start_monitoring(self, interval: float = 1.0):
        """Запустить фоновый мониторинг"""
        self._update_interval = interval
        self._running = True
        
        def monitor_loop():
            while self._running:
                try:
                    snapshot = self.get_snapshot()
                    for callback in self._callbacks:
                        try:
                            callback(snapshot)
                        except Exception as e:
                            print(f"Callback error: {e}")
                except Exception as e:
                    print(f"Monitoring error: {e}")
                
                import time
                time.sleep(self._update_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Остановить мониторинг"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            self._monitor_thread = None

    @property
    def is_running(self) -> bool:
        """Проверить, запущен ли мониторинг"""
        return self._running


# Точка входа для тестирования ядра
if __name__ == "__main__":
    print("=" * 70)
    print("🖥️  System Monitor Core - Тестирование ядра")
    print("=" * 70)
    
    core = SystemMonitorCore()
    
    print("\n📊 Получение снимка системы...")
    snapshot = core.get_snapshot()
    
    print("\n" + "-" * 70)
    print("СИСТЕМНАЯ ИНФОРМАЦИЯ:")
    print("-" * 70)
    print(f"  ОС: {snapshot.system.system} {snapshot.system.release}")
    print(f"  Хост: {snapshot.system.node}")
    print(f"  Архитектура: {snapshot.system.machine}")
    print(f"  Процессор: {snapshot.system.processor}")
    print(f"  Время работы: {snapshot.system.uptime_seconds / 3600:.2f} часов")
    print(f"  Python: {snapshot.system.python_version}")
    
    print("\n" + "-" * 70)
    print("CPU:")
    print("-" * 70)
    print(f"  Загрузка: {snapshot.cpu.usage_percent:.1f}%")
    print(f"  Ядра: {snapshot.cpu.cores_physical} физических / {snapshot.cpu.cores_logical} логических")
    print(f"  Частота: {snapshot.cpu.freq_current:.0f} МГц (макс: {snapshot.cpu.freq_max:.0f} МГц)")
    if snapshot.cpu.load_avg_1 > 0:
        print(f"  Load Average: {snapshot.cpu.load_avg_1:.2f}, {snapshot.cpu.load_avg_5:.2f}, {snapshot.cpu.load_avg_15:.2f}")
    
    print("\n" + "-" * 70)
    print("ПАМЯТЬ:")
    print("-" * 70)
    print(f"  Всего: {snapshot.memory.total / (1024**3):.2f} GB")
    print(f"  Использовано: {snapshot.memory.used / (1024**3):.2f} GB ({snapshot.memory.percent:.1f}%)")
    print(f"  Доступно: {snapshot.memory.available / (1024**3):.2f} GB")
    if snapshot.memory.swap_total > 0:
        print(f"  Swap: {snapshot.memory.swap_used / (1024**3):.2f} / {snapshot.memory.swap_total / (1024**3):.2f} GB")
    
    print("\n" + "-" * 70)
    print("ДИСК:")
    print("-" * 70)
    for part in snapshot.disk.partitions[:5]:
        print(f"  {part['mountpoint']}: {part['used']/(1024**3):.1f}/{part['total']/(1024**3):.1f} GB ({part['percent']}%)")
    
    print("\n" + "-" * 70)
    print("СЕТЬ:")
    print("-" * 70)
    print(f"  Отправлено: {snapshot.network.bytes_sent / (1024**2):.2f} MB")
    print(f"  Получено: {snapshot.network.bytes_recv / (1024**2):.2f} MB")
    print(f"  IP адрес: {snapshot.network.ip_address}")
    
    print("\n" + "-" * 70)
    print("ПРОЦЕССЫ:")
    print("-" * 70)
    print(f"  Всего: {snapshot.processes.total_processes}")
    print(f"  Активных: {snapshot.processes.running_processes}")
    print("  Top по CPU:")
    for proc in snapshot.processes.top_cpu_processes[:5]:
        print(f"    {proc['name']}: {proc['cpu_percent']:.1f}%")
    
    if snapshot.gpu.available:
        print("\n" + "-" * 70)
        print("GPU:")
        print("-" * 70)
        print(f"  Название: {snapshot.gpu.gpu_name}")
        print(f"  Загрузка: {snapshot.gpu.gpu_load}%")
        print(f"  Память: {snapshot.gpu.gpu_memory_used/(1024**2):.0f} / {snapshot.gpu.gpu_memory_total/(1024**2):.0f} MB")
    
    if snapshot.battery.available:
        print("\n" + "-" * 70)
        print("БАТАРЕЯ:")
        print("-" * 70)
        print(f"  Заряд: {snapshot.battery.percent}%")
        print(f"  Питание: {'Подключено' if snapshot.battery.plugged_in else 'От батареи'}")
        print(f"  Осталось: {snapshot.battery.time_left}")
    
    if snapshot.temperature.available:
        print("\n" + "-" * 70)
        print("ТЕМПЕРАТУРА:")
        print("-" * 70)
        for sensor_name, sensors in snapshot.temperature.sensors.items():
            for sensor in sensors[:3]:
                print(f"  {sensor_name} - {sensor['label']}: {sensor['current']}°C")
    
    print("\n" + "=" * 70)
    print("✅ Тестирование ядра завершено успешно!")
    print("=" * 70)
    
    # Сохраняем полный отчет в JSON
    with open('system_report.json', 'w', encoding='utf-8') as f:
        f.write(core.to_json())
    print(f"\n📁 Полный отчет сохранен в: system_report.json")
