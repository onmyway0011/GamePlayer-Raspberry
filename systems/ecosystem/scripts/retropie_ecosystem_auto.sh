#!/bin/bash

# retropie_ecosystem_auto.sh
# 全自动RetroPie游戏生态优化脚本（零交互）
# 日志：retropie_ecosystem_auto.log

LOGFILE="retropie_ecosystem_auto.log"
ROLLBACK_ACTIONS=()

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOGFILE"
}

rollback() {
    log "执行回滚操作..."
    for (( idx=${#ROLLBACK_ACTIONS[@]}-1 ; idx>=0 ; idx-- )) ; do
        eval "${ROLLBACK_ACTIONS[idx]}"
    done
    log "回滚完成。"
}

trap 'log "检测到错误，开始回滚..."; rollback; exit 1' ERR

set -e

log "=== RetroPie 游戏生态全自动优化开始 ==="

# 0. 网络与依赖检测
log "[0/6] 网络与依赖检测"
ping -c 1 www.google.com >/dev/null 2>&1 || { log "网络不可用，请检查网络连接。"; exit 1; }
for cmd in mono unzip git curl rclone; do
    if ! command -v $cmd >/dev/null 2>&1; then
        log "缺少依赖：$cmd，正在安装..."
        sudo apt update
        sudo apt install -y $cmd
    fi
done

# 1. 多平台Skraper自动封面与元数据（自动profile生成）
log "[1/6] 多平台Skraper自动封面与元数据"
ROM_ROOT="/home/pi/RetroPie/roms"
PLATFORMS=($(ls "$ROM_ROOT"))
cd "$HOME"
if [ ! -d skraper ]; then
    wget -O Skraper_Linux.zip https://www.skraper.net/Skraper_Linux.zip
    unzip -o Skraper_Linux.zip -d skraper
fi
cd skraper
for SYS in "${PLATFORMS[@]}"; do
    PROFILE="profile_${SYS}.ini"
    if [ ! -f "$PROFILE" ]; then
        cat > "$PROFILE" <<EOF
[General]
Platform=$SYS
RomPath=$ROM_ROOT/$SYS
OutputPath=$ROM_ROOT/$SYS
EOF
        log "[$SYS] 已自动生成profile_${SYS}.ini"
    fi
    if [ ! -d "$ROM_ROOT/$SYS/media" ] || [ ! -f "$ROM_ROOT/$SYS/gamelist.xml" ]; then
        mono Skraper.Console.exe --profile "$PROFILE" --output "$ROM_ROOT/$SYS" | tee -a "$LOGFILE"
        log "[$SYS] Skraper封面与元数据已批量抓取。"
        ROLLBACK_ACTIONS+=("rm -rf '$ROM_ROOT/$SYS/media' '$ROM_ROOT/$SYS/gamelist.xml'; log '已删除$SYS封面与元数据。'")
    else
        log "[$SYS] 封面与元数据已存在，跳过。"
    fi
    sleep 1
    done
cd ..

# 2. 主题批量安装与自动切换
log "[2/6] 主题批量安装与自动切换"
THEME_DIR="/etc/emulationstation/themes"
mkdir -p "$THEME_DIR"
sudo ~/RetroPie-Setup/retropie_packages.sh esthemes install
THEME_LIST=(
    "epicnoir|https://github.com/lipebello/es-theme-epicnoir.git"
    "RetroPie-Material|https://github.com/DwayneHurst/RetroPie-Material.git"
    "simple|https://github.com/RetroPie/es-theme-simple.git"
)
for THEME in "${THEME_LIST[@]}"; do
    NAME="${THEME%%|*}"
    URL="${THEME##*|}"
    if [ ! -d "$THEME_DIR/$NAME" ]; then
        git clone "$URL" "$THEME_DIR/$NAME" || true
        log "已安装主题：$NAME"
    fi
    sleep 1
    done
THEME_CFG=~/.emulationstation/es_settings.cfg
cp "$THEME_CFG" "$THEME_CFG.bak.$(date +%s)"
sed -i '/^<string name="ThemeSet"/d' "$THEME_CFG"
echo '<string name="ThemeSet" value="RetroPie-Material" />' >> "$THEME_CFG"
log "已自动切换到主题：RetroPie-Material"
ROLLBACK_ACTIONS+=("cp '$THEME_CFG.bak.*' '$THEME_CFG'; log '已恢复主题设置。'")

# 3. Netplay多平台自动配置
log "[3/6] Netplay多平台自动配置"
for SYS in "${PLATFORMS[@]}"; do
    CFG="/opt/retropie/configs/$SYS/retroarch.cfg"
    if [ -f "$CFG" ]; then
        sudo cp "$CFG" "$CFG.bak.$(date +%s)"
        sudo sed -i '/^netplay_mode =/d' "$CFG"
        sudo sed -i '/^netplay_ip_port =/d' "$CFG"
        echo 'netplay_mode = "false"' | sudo tee -a "$CFG"
        echo 'netplay_ip_port = "55435"' | sudo tee -a "$CFG"
        log "[$SYS] 已配置Netplay端口为55435。"
        ROLLBACK_ACTIONS+=("cp '$CFG.bak.*' '$CFG'; log '已恢复$SYS Netplay配置。'")
    fi
    sleep 1
    done

# 4. 云存档多平台自动挂载（自动检测rclone远程名）
log "[4/6] 云存档多平台自动挂载"
RCLONE_REMOTE=$(rclone listremotes | head -n1 | sed 's/://')
if [ -n "$RCLONE_REMOTE" ]; then
    mkdir -p ~/cloud_saves
    rclone mount "$RCLONE_REMOTE":/retropie_saves ~/cloud_saves --daemon
    for SYS in "${PLATFORMS[@]}"; do
        SAVES="$ROM_ROOT/$SYS/saves"
        mkdir -p ~/cloud_saves/$SYS
        if [ ! -L "$SAVES" ]; then
            mv "$SAVES"/* ~/cloud_saves/$SYS/ 2>/dev/null || true
            rm -rf "$SAVES"
            ln -s ~/cloud_saves/$SYS "$SAVES"
            log "[$SYS] 存档目录已映射到云端。"
            ROLLBACK_ACTIONS+=("rm -rf '$SAVES'; mkdir -p '$SAVES'; log '已取消$SYS云存档映射。'")
        else
            log "[$SYS] 存档已映射到云端，跳过。"
        fi
        sleep 1
        done
else
    log "未检测到rclone远程，跳过云存档挂载。"
fi

# 5. 检查所有优化项是否已完成
log "[5/6] 检查所有优化项是否已完成"
ALL_OPTIMIZED=1
for SYS in "${PLATFORMS[@]}"; do
    if [ ! -d "$ROM_ROOT/$SYS/media" ] || [ ! -f "$ROM_ROOT/$SYS/gamelist.xml" ]; then
        ALL_OPTIMIZED=0
    fi
    CFG="/opt/retropie/configs/$SYS/retroarch.cfg"
    if [ -f "$CFG" ] && ! grep -q 'netplay_ip_port = "55435"' "$CFG"; then
        ALL_OPTIMIZED=0
    fi
    SAVES="$ROM_ROOT/$SYS/saves"
    if [ ! -L "$SAVES" ] && [ -d "$SAVES" ]; then
        ALL_OPTIMIZED=0
    fi
    done
if ! grep -q 'RetroPie-Material' "$THEME_CFG"; then
    ALL_OPTIMIZED=0
fi

if [ $ALL_OPTIMIZED -eq 1 ]; then
    log "所有优化项已完成，无需进一步优化。"
else
    log "检测到未完成优化项，建议重新运行本脚本。"
fi

log "=== 游戏生态全自动优化完成 ==="
echo "如遇异常，日志见 $LOGFILE"
echo "如需回滚，重新运行本脚本。" 