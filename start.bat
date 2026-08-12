@echo off
chcp 65001 >nul
title AI4Video

echo ========================================
echo   AI4Video - 多路视频智能分析平台
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    pause
    exit /b 1
)

:: 检查 uv（推荐）
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] 使用 uv 启动...
    echo.
    uv run python manage.py runserver 0.0.0.0:10001
) else (
    echo [信息] 使用 python 启动...
    echo.
    python manage.py runserver 0.0.0.0:10001
)

pause
