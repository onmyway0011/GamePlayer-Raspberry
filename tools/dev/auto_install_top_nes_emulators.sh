#!/bin/bash
# 一键下载并集成Mesen、puNES、Nestopia UE（macOS/Linux通用）
# 集成目录：/opt/emulators
# 自动软链到/usr/local/bin
set -e

EMUDIR="/opt/emulators"
mkdir -p "$EMUDIR"

# 检测平台
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

# 下载Mesen
MESEN_URL="https://github.com/SourMesen/Mesen/releases/latest/download/mesen-linux-x64.tar.gz"
MESEN_APP="mesen"
if [[ "$OS" == "darwin" ]]; then
  MESEN_URL="https://github.com/SourMesen/Mesen/releases/latest/download/mesen-macos-universal.zip"
  MESEN_APP="Mesen.app/Contents/MacOS/Mesen"
fi
cd "$EMUDIR"
echo "下载Mesen..."
curl -L -o mesen.tar.gz "$MESEN_URL" || curl -L -o mesen.zip "$MESEN_URL"
if [[ -f mesen.tar.gz ]]; then
  tar -xzf mesen.tar.gz || unzip mesen.tar.gz
  rm -f mesen.tar.gz
elif [[ -f mesen.zip ]]; then
  unzip mesen.zip
  rm -f mesen.zip
fi

# 下载puNES
PUNES_URL="https://github.com/punesemu/puNES/releases/latest/download/puNES-x86_64.AppImage"
if [[ "$OS" == "darwin" ]]; then
  PUNES_URL="https://github.com/punesemu/puNES/releases/latest/download/puNES-macOS.zip"
fi
echo "下载puNES..."
curl -L -o punes.AppImage "$PUNES_URL" || curl -L -o punes.zip "$PUNES_URL"
if [[ -f punes.AppImage ]]; then
  chmod +x punes.AppImage
elif [[ -f punes.zip ]]; then
  unzip punes.zip
  rm -f punes.zip
fi

# 下载Nestopia UE
NESTOPIA_URL="https://github.com/0ldsk00l/nestopia/releases/latest/download/nestopia-1.52.1.tar.gz"
if [[ "$OS" == "darwin" ]]; then
  NESTOPIA_URL="https://github.com/0ldsk00l/nestopia/releases/latest/download/nestopia-1.52.1-macos.zip"
fi
echo "下载Nestopia UE..."
curl -L -o nestopia.tar.gz "$NESTOPIA_URL" || curl -L -o nestopia.zip "$NESTOPIA_URL"
if [[ -f nestopia.tar.gz ]]; then
  tar -xzf nestopia.tar.gz || unzip nestopia.tar.gz
  rm -f nestopia.tar.gz
elif [[ -f nestopia.zip ]]; then
  unzip nestopia.zip
  rm -f nestopia.zip
fi

# 自动软链到/usr/local/bin
if [[ -f "$EMUDIR/$MESEN_APP" ]]; then
  ln -sf "$EMUDIR/$MESEN_APP" /usr/local/bin/mesen
fi
if [[ -f "$EMUDIR/punes.AppImage" ]]; then
  ln -sf "$EMUDIR/punes.AppImage" /usr/local/bin/punes
fi
if [[ -f "$EMUDIR/nestopia" ]]; then
  ln -sf "$EMUDIR/nestopia" /usr/local/bin/nestopia
fi

echo "✅ Mesen、puNES、Nestopia UE 已集成到/opt/emulators，并自动软链到/usr/local/bin。" 