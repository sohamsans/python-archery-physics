@echo off
title Archery Aerodynamics Simulator
echo Starting Simulator...
echo.

python src\gui.py

if %errorlevel% neq 0 (
    echo.
    echo ---------------------------------------------------
    echo Error encountered! output is shown above.
    echo ---------------------------------------------------
    pause
)
