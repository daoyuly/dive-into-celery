#!/bin/bash

# Celery Worker 启动脚本

echo "启动 Celery Worker..."

# 启动基础队列的 worker
celery -A celery_app worker \
    --loglevel=info \
    --queues=basic,advanced,realworld \
    --concurrency=4 \
    --hostname=worker@%h \
    --pool=prefork \
    --max-tasks-per-child=1000

