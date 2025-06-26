@echo off
chcp 65001 >nul
echo === RetroPie 安装器快速安装 ===
echo 正在检查系统环境...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ 找到 Python: %PYTHON_VERSION%

REM 检查pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 未找到 pip，请先安装 pip
    pause
    exit /b 1
)
echo ✓ 找到 pip

REM 安装Python依赖
echo 正在安装Python依赖...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ✗ Python依赖安装失败
    pause
    exit /b 1
)
echo ✓ Python依赖安装成功

REM 运行测试
echo 正在运行功能测试...
python test_installer.py

echo.
echo === 安装完成 ===
echo 使用方法:
echo   python retropie_installer.py --help     # 查看帮助
echo   python retropie_installer.py --check-only    # 检查依赖
echo   python retropie_installer.py --download-only # 仅下载镜像
echo.
echo 注意: Windows系统需要手动使用烧录工具
echo 推荐工具: Win32DiskImager 或 balenaEtcher
pause 