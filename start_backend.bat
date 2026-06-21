@echo off
echo Dang khoi dong Backend...
cd /d E:\QUANLYTRUONGHOC
uvicorn main_api:app --reload --port 8000
pause
