#!/bin/bash
# 房地产Agent SaaS管理平台 - 启动脚本
# 适用环境：Linux/Unix

APP_NAME="real_estate_agent_saas"
APP_DIR=$(cd "$(dirname "$0")" && pwd)
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/$APP_NAME.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到python3，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$APP_DIR/venv" ]; then
    echo "检测到虚拟环境不存在，正在创建..."
    python3 -m venv "$APP_DIR/venv"
    echo "虚拟环境创建完成，正在安装依赖..."
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo "依赖安装完成"
fi

# 读取环境变量（精准匹配行首变量，解决多PORT匹配bug）
APP_HOST=$(grep '^HOST=' .env | cut -d'=' -f2)
APP_PORT=$(grep '^PORT=' .env | cut -d'=' -f2)
APP_WORKERS=$(grep '^WORKERS=' .env | cut -d'=' -f2)

# 启动服务
echo "正在启动 $APP_NAME..."
cd "$APP_DIR"
"$APP_DIR/venv/bin/uvicorn" main:app \
--host "$APP_HOST" \
--port "$APP_PORT" \
--workers "$APP_WORKERS" \
--log-level info \
--log-config "$APP_DIR/logging.conf" 2>&1 | tee "$LOG_DIR/access.log" &

# 保存PID
echo $! > "$PID_FILE"
echo "$APP_NAME 启动成功，PID: $(cat $PID_FILE)"
echo "访问地址：http://$APP_HOST:$APP_PORT/docs"
