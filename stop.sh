#!/bin/bash

# 房地产Agent SaaS管理平台 - 停止脚本
# 适用环境：Linux/Unix

APP_NAME="real_estate_agent_saas"
APP_DIR=$(cd "$(dirname "$0")" && pwd)
PID_FILE="$APP_DIR/$APP_NAME.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "错误：未找到PID文件，服务可能未运行"
    exit 1
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo "正在停止 $APP_NAME (PID: $PID)..."
    kill "$PID"
    sleep 2
    
    # 检查进程是否已停止
    if kill -0 "$PID" 2>/dev/null; then
        echo "进程未停止，强制终止..."
        kill -9 "$PID"
    fi
    
    rm -f "$PID_FILE"
    echo "$APP_NAME 已停止"
else
    echo "$APP_NAME 服务未运行"
    rm -f "$PID_FILE"
fi
