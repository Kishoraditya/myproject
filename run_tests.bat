@echo off
setlocal

REM Run tests with the appropriate Django settings
set DJANGO_SETTINGS_MODULE=myproject.settings.test
python run_tests.py %*

endlocal 