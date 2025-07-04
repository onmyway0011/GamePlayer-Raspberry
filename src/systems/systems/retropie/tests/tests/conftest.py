import pytest

@pytest.fixture(autouse=True)


def auto_patch_input(monkeypatch):
    """TODO: 添加文档字符串"""
    monkeypatch.setattr('builtins.input', lambda *a, **k: 'yes')
