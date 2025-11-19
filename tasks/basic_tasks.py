"""
基础任务示例

这个模块展示了 Celery 的基础用法：
1. 简单任务定义
2. 带参数的任务
3. 任务异步调用
4. 获取任务结果
5. 定时任务
"""

from celery_app import app
import time
from datetime import datetime

@app.task(name='tasks.basic_tasks.hello_world')
def hello_world(x, y):
    """
    简单的 Hello World 任务
    """
    time.sleep(2)
    return f"hello_world: {x} + {y} = {x + y}"

@app.task(name='tasks.basic_tasks.add')
def add(x, y):
    """
    简单的加法任务
    
    这个任务展示了最基本的 Celery 任务定义和使用
    """
    print(f"计算 {x} + {y}")
    result = x + y
    print(f"结果: {result}")
    return result


@app.task(name='tasks.basic_tasks.multiply')
def multiply(x, y):
    """
    乘法任务，模拟耗时操作
    """
    print(f"计算 {x} * {y}")
    time.sleep(2)  # 模拟耗时操作
    result = x * y
    print(f"结果: {result}")
    return result


@app.task(name='tasks.basic_tasks.process_data')
def process_data(data_list):
    """
    处理数据列表的任务
    
    参数:
        data_list: 要处理的数据列表
    """
    print(f"开始处理 {len(data_list)} 条数据")
    processed = []
    for item in data_list:
        # 模拟数据处理
        processed.append(f"processed_{item}")
        time.sleep(0.5)
    print(f"处理完成，共 {len(processed)} 条")
    return processed


@app.task(name='tasks.basic_tasks.periodic_task')
def periodic_task():
    """
    定时任务示例 - 每30秒执行一次
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[定时任务] 执行时间: {current_time}")
    return f"定时任务执行于 {current_time}"


@app.task(name='tasks.basic_tasks.daily_task')
def daily_task():
    """
    每日任务示例 - 每天凌晨2点执行
    """
    print("[每日任务] 执行每日维护任务")
    return "每日任务执行完成"


@app.task(name='tasks.basic_tasks.weekly_task')
def weekly_task():
    """
    每周任务示例 - 每周一上午9点执行
    """
    print("[每周任务] 执行周报生成任务")
    return "周报生成完成"


@app.task(name='tasks.basic_tasks.long_running_task', bind=True)
def long_running_task(self, duration=10):
    """
    长时间运行的任务，支持进度更新
    
    参数:
        self: 任务实例（使用 bind=True 时自动注入）
        duration: 任务持续时间（秒）
    
    这个任务展示了如何更新任务状态和进度
    """
    total_steps = duration
    for i in range(total_steps):
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_steps,
                'percent': int((i + 1) / total_steps * 100)
            }
        )
        print(f"进度: {i + 1}/{total_steps} ({int((i + 1) / total_steps * 100)}%)")
        time.sleep(1)
    
    return {
        'current': total_steps,
        'total': total_steps,
        'percent': 100,
        'status': '任务完成'
    }

