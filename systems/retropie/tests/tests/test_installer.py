import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../core')))
from retropie_installer import RetroPieInstaller

class DummyResp:
    text = 'retropie-buster-4.8-rpi4_400.img.gz'
    def raise_for_status(self): pass

def test_check_dependencies(monkeypatch):
    installer = RetroPieInstaller()
    monkeypatch.setattr(installer, '_run_command', lambda *a, **k: (0, 'dd', ''))
    assert installer.check_dependencies() is True

def test_get_download_url(monkeypatch):
    installer = RetroPieInstaller()
    monkeypatch.setattr('requests.get', lambda *a, **k: DummyResp())
    url = installer.get_retropie_download_url()
    assert url and url.endswith('.img.gz')

def test_list_available_disks(monkeypatch):
    installer = RetroPieInstaller()
    monkeypatch.setattr(installer, '_list_unix_disks', lambda: [('/dev/sda', '32G', 'Unmounted')])
    disks = installer.list_available_disks()
    assert disks and disks[0][0] == '/dev/sda' 