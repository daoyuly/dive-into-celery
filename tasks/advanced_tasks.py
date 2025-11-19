"""
高级任务示例

这个模块展示了 Celery 的高级特性：
1. 任务链（Chain）- 顺序执行多个任务
2. 任务组（Group）- 并行执行多个任务
3. 任务签名（Signature）- 延迟执行任务
4. 回调任务（Callback）
5. 任务重试机制
"""

from celery_app import app
from celery import chain, group, chord
import time
import random


@app.task(name='tasks.advanced_tasks.fetch_data')
def fetch_data(source):
    """
    模拟从数据源获取数据
    """
    print(f"从 {source} 获取数据...")
    time.sleep(1)
    data = [f"data_{i}" for i in range(5)]
    print(f"获取到 {len(data)} 条数据")
    return data


@app.task(name='tasks.advanced_tasks.process_item')
def process_item(item):
    """
    处理单个数据项
    """
    print(f"处理: {item}")
    time.sleep(0.5)
    return f"processed_{item}"


@app.task(name='tasks.advanced_tasks.save_result')
def save_result(result):
    """
    保存处理结果
    """
    print(f"保存结果: {result}")
    time.sleep(1)
    return f"saved_{result}"


@app.task(name='tasks.advanced_tasks.aggregate_results')
def aggregate_results(results):
    """
    聚合多个任务的结果
    """
    print(f"聚合 {len(results)} 个结果")
    aggregated = {
        'total': len(results),
        'results': results,
        'timestamp': time.time()
    }
    return aggregated


@app.task(name='tasks.advanced_tasks.task_with_retry', bind=True, max_retries=3)
def task_with_retry(self, value):
    """
    带重试机制的任务
    
    参数:
        self: 任务实例
        value: 输入值
    
    这个任务有50%的概率失败，失败后会自动重试
    """
    print(f"执行任务，输入值: {value}")
    
    # 模拟随机失败
    if random.random() < 0.5:
        print("任务失败，准备重试...")
        # 重试任务，延迟2秒
        raise self.retry(countdown=2, exc=Exception("模拟的失败"))
    
    print("任务成功完成")
    return f"处理成功: {value}"


@app.task(name='tasks.advanced_tasks.task_with_custom_retry', bind=True, max_retries=5)
def task_with_custom_retry(self, url):
    """
    自定义重试逻辑的任务
    
    根据不同的错误类型采用不同的重试策略
    """
    print(f"请求 URL: {url}")
    
    # 模拟不同类型的错误
    error_type = random.choice(['timeout', 'connection', 'success'])
    
    if error_type == 'timeout':
        print("超时错误")
        # 超时错误：指数退避重试
        retry_delay = 2 ** self.request.retries
        raise self.retry(countdown=retry_delay, exc=Exception("超时错误"))
    elif error_type == 'connection':
        print("连接错误")
        # 连接错误：固定延迟重试
        raise self.retry(countdown=5, exc=Exception("连接错误"))
    else:
        print("请求成功")
        return f"成功获取 {url} 的数据"


@app.task(name='tasks.advanced_tasks.on_chord_error', bind=True)
def on_chord_error(self, request, exc, traceback):
    """
    Chord 错误回调任务
    """
    print(f"Chord 任务组执行出错: {exc}")
    return f"错误处理完成: {exc}"


def create_task_chain_example():
    """
    创建任务链示例
    
    任务链会按顺序执行：
    fetch_data -> process_item -> save_result
    """
    # 方式1: 使用 chain 函数
    workflow = chain(
        fetch_data.s('database'),
        process_item.s(),
        save_result.s()
    )
    return workflow


def create_task_group_example():
    """
    创建任务组示例
    
    任务组会并行执行多个任务
    """
    # 并行处理多个数据源
    job = group(
        fetch_data.s('source1'),
        fetch_data.s('source2'),
        fetch_data.s('source3'),
    )
    return job


def create_chord_example():
    """
    创建 Chord 示例
    
    Chord = Group + Callback
    先并行执行一组任务，然后执行回调任务聚合结果
    """
    # 并行处理多个项目，然后聚合结果
    callback = aggregate_results.s()
    header = [
        process_item.s('item1'),
        process_item.s('item2'),
        process_item.s('item3'),
        process_item.s('item4'),
    ]
    chord_task = chord(header)(callback)
    return chord_task

