@echo off
chcp 65001 >nul
title AI4Video - 启动中...

echo ========================================
echo   AI4Video - 多路视频智能分析平台
echo ========================================
echo.

:: 启动 ZLMediaKit
set ZLM_PATH=zlm\bin.x86.windows10\ai4video_zlm.exe
if exist "%ZLM_PATH%" (
    echo [1/2] 启动 ZLMediaKit...
    start "" "%ZLM_PATH%"
    timeout /t 2 >nul
    echo [✓] ZLMediaKit 已启动
) else (
    echo [!] ZLMediaKit 未找到，跳过
)
echo.

:: 启动 Django
echo [2/2] 启动 AI4Video...
echo.
echo 访问地址: http://localhost:10001/
echo 默认账号: admin
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

where uv >nul 2>&1
if %errorlevel% equ 0 (
    uv run python manage.py runserver 0.0.0.0:10001
) else (
    python manage.py runserver 0.0.0.0:10001
)

pause
