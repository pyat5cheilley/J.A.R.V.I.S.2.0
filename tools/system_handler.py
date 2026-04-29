"""System information and control handler for J.A.R.V.I.S."""

import platform
import psutil
import datetime
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """Return basic system information."""
    uname = platform.uname()
    return {
        "system": uname.system,
        "node": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
    }


def get_cpu_usage() -> Dict[str, Any]:
    """Return current CPU usage statistics."""
    return {
        "percent": psutil.cpu_percent(interval=1),
        "count_logical": psutil.cpu_count(logical=True),
        "count_physical": psutil.cpu_count(logical=False),
        "frequency_mhz": round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else None,
    }


def get_memory_usage() -> Dict[str, Any]:
    """Return current RAM usage statistics."""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "percent": mem.percent,
    }


def get_disk_usage(path: str = "/") -> Dict[str, Any]:
    """Return disk usage for the given path."""
    disk = psutil.disk_usage(path)
    return {
        "path": path,
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
    }


def get_uptime() -> str:
    """Return system uptime as a human-readable string."""
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    delta = datetime.datetime.now() - boot_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def format_system_report() -> str:
    """Build a human-readable system status report."""
    info = get_system_info()
    cpu = get_cpu_usage()
    mem = get_memory_usage()
    disk = get_disk_usage()
    uptime = get_uptime()

    lines = [
        f"System  : {info['system']} {info['release']} ({info['machine']})",
        f"Host    : {info['node']}",
        f"Uptime  : {uptime}",
        f"CPU     : {cpu['percent']}% used  |  {cpu['count_logical']} logical cores",
        f"Memory  : {mem['used_gb']} GB / {mem['total_gb']} GB  ({mem['percent']}%)",
        f"Disk    : {disk['used_gb']} GB / {disk['total_gb']} GB  ({disk['percent']}%)",
    ]
    return "\n".join(lines)
