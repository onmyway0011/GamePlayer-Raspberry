import pytest

@pytest.fixture(autouse=True)


def auto_patch_input(monkeypatch):
    """TODO: Add docstring"""
    monkeypatch.setattr('builtins.input', lambda *a, **k: 'yes')
