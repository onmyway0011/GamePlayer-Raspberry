import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../roms')))
from rom_downloader import ROMDownloader

class DummyResp:
    def json(self):
        return {'response': {'docs': [{'downloads': 1, 'identifier': 'id', 'title': 't', 'description': '', 'files': []}]}}
    def raise_for_status(self): pass

def test_load_config(tmp_path):
    config_path = tmp_path / 'rom_config.json'
    downloader = ROMDownloader(str(config_path))
    assert downloader.config

def test_search_roms(monkeypatch):
    downloader = ROMDownloader()
    monkeypatch.setattr(downloader.session, 'get', lambda *a, **k: DummyResp())
    results = downloader.search_roms()
    assert results and results[0]['identifier'] == 'id' 