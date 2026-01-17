#!/bin/bash
cd /home/ubuntu/RealTime_ChatApp
pkill -f "python3 app.py" 2>/dev/null || true
sleep 1
/home/ubuntu/RealTime_ChatApp/venv/bin/python3 app.py > output.log 2>&1 &
echo $! > /home/ubuntu/RealTime_ChatApp/app.pid
sleep 2
echo "App started with PID $(cat /home/ubuntu/RealTime_ChatApp/app.pid)"
