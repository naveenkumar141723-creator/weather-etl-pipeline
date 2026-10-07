@echo off
E:
cd E:\Python
E:\Python\.venv\Scripts\python.exe E:\Python\ETLweather.py
echo Pipeline completed at %date% %time% >> E:\Python\pipeline_log.txt