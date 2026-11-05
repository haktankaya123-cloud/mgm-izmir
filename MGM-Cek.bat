@echo off
chcp 65001 >nul
title MGM Izmir - Veri Cekimi
cd /d "%~dp0"

set PY=python
where py >nul 2>nul && set PY=py -3

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python bulunamadi. python.org adresinden kurup "Add to PATH" kutusunu isaretle.
    pause
    exit /b 1
)

%PY% -c "import requests" >nul 2>nul
if errorlevel 1 (
    echo requests kutuphanesi kuruluyor...
    %PY% -m pip install --quiet requests
)

%PY% mgm-veri.py
if errorlevel 1 (
    echo.
    echo Cekim basarisiz. Ayrinti icin mgm-log.txt dosyasina bak.
    pause
)
