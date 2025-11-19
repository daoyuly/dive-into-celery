"""
简单的 Celery 任务演示

演示如何调用 Celery 任务并获取结果
"""

import sys
from pathlib import Path
import time
import random
# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app 
from tasks.basic_tasks import hello_world, add


if __name__ == '__main__':
    print("=" * 60)
    print("Celery 任务演示")
    print("=" * 60)
    print("\n💡 提示: 请确保 Celery Worker 正在运行")
    print("   启动命令: celery -A celery_app worker --loglevel=info")
    print("=" * 60 + "\n")
    
    while True:
        i = random.randint(1, 100)
        result = hello_world.delay(i, i)
        value = result.get(timeout=5)
        print(value)
        time.sleep(2)
    