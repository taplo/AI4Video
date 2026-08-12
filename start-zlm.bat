@echo off
chcp 65001 >nul
title ZLMediaKit

echo ========================================
echo   ZLMediaKit - 流媒体服务器
echo ========================================
echo.

set ZLM_PATH=zlm\bin.x86.windows10\ai4video_zlm.exe

if not exist "%ZLM_PATH%" (
    echo [错误] 未找到 ZLMediaKit: %ZLM_PATH%
    pause
    exit /b 1
)

echo [信息] 启动 ZLMediaKit...
echo.
start "" "%ZLM_PATH%"

timeout /t 2 >nul
echo [信息] ZLMediaKit 已启动
echo.
pause
