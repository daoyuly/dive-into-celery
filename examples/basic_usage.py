"""
基础用法示例

演示如何调用 Celery 任务并获取结果
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from tasks.basic_tasks import add, multiply, process_data, long_running_task
import time


def example_simple_task():
    """简单任务调用示例"""
    print("=" * 50)
    print("示例1: 简单任务调用")
    print("=" * 50)
    
    # 异步调用任务
    result = add.delay(4, 5)
    print(f"任务ID: {result.id}")
    print(f"任务状态: {result.state}")
    
    # 等待任务完成并获取结果
    print("等待任务完成...")
    value = result.get(timeout=10)
    print(f"任务结果: {value}")
    print(f"最终状态: {result.state}\n")


def example_task_with_wait():
    """带等待的任务调用"""
    print("=" * 50)
    print("示例2: 耗时任务调用")
    print("=" * 50)
    
    result = multiply.delay(6, 7)
    print(f"任务已提交，ID: {result.id}")
    
    # 轮询任务状态
    while not result.ready():
        print(f"任务状态: {result.state}")
        time.sleep(0.5)
    
    print(f"任务完成，结果: {result.get()}\n")


def example_batch_processing():
    """批量处理示例"""
    print("=" * 50)
    print("示例3: 批量处理")
    print("=" * 50)
    
    data_list = [f"item_{i}" for i in range(5)]
    result = process_data.delay(data_list)
    
    print(f"批量处理任务已提交")
    print(f"结果: {result.get(timeout=30)}\n")


def example_long_running_with_progress():
    """长时间运行任务与进度跟踪"""
    print("=" * 50)
    print("示例4: 长时间运行任务（带进度）")
    print("=" * 50)
    
    result = long_running_task.delay(duration=5)
    print(f"任务ID: {result.id}")
    
    # 轮询进度
    while not result.ready():
        info = result.info
        if isinstance(info, dict) and 'percent' in info:
            print(f"进度: {info['percent']}% ({info.get('current', 0)}/{info.get('total', 0)})")
        time.sleep(1)
    
    print(f"任务完成: {result.get()}\n")


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Celery 基础用法示例")
    print("=" * 50 + "\n")
    
    # 运行示例
    example_simple_task()
    example_task_with_wait()
    example_batch_processing()
    example_long_running_with_progress()
    
    print("所有示例执行完成！")

