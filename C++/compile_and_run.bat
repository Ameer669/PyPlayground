@echo off
set cpp_file=%1
set exe_file=%~n1_program.exe

echo Compiling %cpp_file% to %exe_file%...
"C:\msys64\ucrt64\bin\g++.exe" -g %cpp_file% -o %exe_file%

if errorlevel 1 (
    echo Compilation failed!
    pause
    exit /b %errorlevel%
)

echo Running %exe_file%...
%exe_file%
pause 