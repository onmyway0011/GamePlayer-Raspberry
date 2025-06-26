#!/usr/bin/env python3
"""
GamePlayer-Raspberry 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gameplayer-raspberry",
    version="3.0.0",
    author="GamePlayer Team",
    author_email="team@gameplayer.dev",
    description="Enhanced NES Game Player for Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Emulators",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gameplayer=scripts.nes_game_launcher:main",
            "gameplayer-install=scripts.smart_installer:main",
            "gameplayer-rom=scripts.rom_manager:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
