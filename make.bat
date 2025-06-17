@echo off
REM Makefile equivalent for Windows

if "%1"=="install" (
    echo Installing package in development mode...
    pip install -e .
    pip install -r requirements-dev.txt
    goto :eof
)

if "%1"=="test" (
    echo Running tests...
    pytest tests/ -v
    goto :eof
)

if "%1"=="lint" (
    echo Running linters...
    black --check src/ tests/
    isort --check-only src/ tests/
    flake8 src/ tests/
    mypy src/
    goto :eof
)

if "%1"=="format" (
    echo Formatting code...
    black src/ tests/
    isort src/ tests/
    goto :eof
)

if "%1"=="clean" (
    echo Cleaning build artifacts...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist *.egg-info rmdir /s /q *.egg-info
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    goto :eof
)

if "%1"=="build" (
    echo Building package...
    python -m build
    goto :eof
)

if "%1"=="upload-test" (
    echo Uploading to test PyPI...
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    goto :eof
)

if "%1"=="upload" (
    echo Uploading to PyPI...
    twine upload dist/*
    goto :eof
)

echo Usage: make.bat [install^|test^|lint^|format^|clean^|build^|upload-test^|upload]
