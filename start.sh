#!/bin/bash

function detect_platform(){
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
            echo "mac_arm"
        else
            echo "mac_intel"
        fi
    else
       echo "unknown"
    fi
}

if [ ! -x ".venv/bin/python" ]; then
    echo "未检测到 .venv，请先执行 ./init.sh"
    exit 1
fi

# 启动后端服务
echo "启动后端主应用..."
cd backend
../.venv/bin/python flasky.py &
BACKEND_PID=$!

echo "启动Socket.IO服务..."
../.venv/bin/python flasky_socketio.py &
SOCKETIO_PID=$!

echo "启动Celery服务..."
platform=$(detect_platform)
case $platform in
    "windows")
        echo "操作系统: Windows"
        ../.venv/bin/python -m celery -A app.make_celery worker -B --loglevel INFO --logfile=logs/celery.log -P eventlet &
        ;;
    "mac_arm"|"mac_intel")
        echo "操作系统: macOS"
        ../.venv/bin/python -m celery -A app.make_celery worker -B --loglevel INFO --logfile=logs/celery.log &
        ;;
    *)
        echo "操作系统: 未知 ($OSTYPE)"
        ;;
esac
CELERY_PID=$!

# 启动前端服务
echo "启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $SOCKETIO_PID $CELERY_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait
