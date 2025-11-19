#!/bin/bash

# Celery Beat 启动脚本（定时任务调度器）

echo "启动 Celery Beat..."

celery -A celery_app beat \
    --loglevel=info

