"""Tests for tools/system_handler.py"""

import pytest
from unittest.mock import patch, MagicMock
import tools.system_handler as sh


def test_get_system_info_keys():
    info = sh.get_system_info()
    for key in ("system", "node", "release", "version", "machine", "processor"):
        assert key in info


def test_get_cpu_usage_structure():
    cpu = sh.get_cpu_usage()
    assert "percent" in cpu
    assert "count_logical" in cpu
    assert isinstance(cpu["percent"], float)
    assert cpu["count_logical"] >= 1


def test_get_memory_usage_values():
    mem = sh.get_memory_usage()
    assert mem["total_gb"] > 0
    assert 0 <= mem["percent"] <= 100
    assert mem["used_gb"] <= mem["total_gb"]


def test_get_disk_usage_default_path():
    disk = sh.get_disk_usage()
    assert disk["path"] == "/"
    assert disk["total_gb"] > 0
    assert 0 <= disk["percent"] <= 100


def test_get_uptime_format():
    uptime = sh.get_uptime()
    assert "h" in uptime
    assert "m" in uptime
    assert "s" in uptime


def test_format_system_report_contains_sections():
    report = sh.format_system_report()
    for section in ("System", "Host", "Uptime", "CPU", "Memory", "Disk"):
        assert section in report


def test_get_cpu_usage_no_freq():
    """Handles machines where cpu_freq() returns None gracefully."""
    with patch("psutil.cpu_freq", return_value=None):
        cpu = sh.get_cpu_usage()
    assert cpu["frequency_mhz"] is None


def test_get_disk_usage_custom_path(tmp_path):
    disk = sh.get_disk_usage(str(tmp_path))
    assert disk["path"] == str(tmp_path)
    assert disk["total_gb"] > 0
