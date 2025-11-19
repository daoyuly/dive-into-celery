"""
高级用法示例

演示任务链、任务组、Chord 等高级特性
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from tasks.advanced_tasks import (
    fetch_data,
    process_item,
    save_result,
    aggregate_results,
    task_with_retry,
    task_with_custom_retry,
    create_task_chain_example,
    create_task_group_example,
    create_chord_example
)
from celery import chain, group, chord
import time


def example_task_chain():
    """任务链示例 - 顺序执行"""
    print("=" * 50)
    print("示例1: 任务链（Chain）- 顺序执行")
    print("=" * 50)
    
    # 方式1: 使用 chain 函数
    workflow = chain(
        fetch_data.s('database'),
        process_item.s(),
        save_result.s()
    )
    
    result = workflow.apply_async()
    print(f"任务链已提交，ID: {result.id}")
    print(f"最终结果: {result.get(timeout=30)}\n")


def example_task_group():
    """任务组示例 - 并行执行"""
    print("=" * 50)
    print("示例2: 任务组（Group）- 并行执行")
    print("=" * 50)
    
    # 并行处理多个数据源
    job = group(
        fetch_data.s('source1'),
        fetch_data.s('source2'),
        fetch_data.s('source3'),
    )
    
    result = job.apply_async()
    print(f"任务组已提交")
    print(f"并行执行结果: {result.get(timeout=30)}\n")


def example_chord():
    """Chord 示例 - 并行执行 + 回调"""
    print("=" * 50)
    print("示例3: Chord - 并行执行后聚合结果")
    print("=" * 50)
    
    # 并行处理多个项目，然后聚合结果
    callback = aggregate_results.s()
    header = [
        process_item.s('item1'),
        process_item.s('item2'),
        process_item.s('item3'),
        process_item.s('item4'),
    ]
    
    chord_task = chord(header)(callback)
    result = chord_task.apply_async()
    
    print(f"Chord 任务已提交")
    print(f"聚合结果: {result.get(timeout=30)}\n")


def example_task_retry():
    """任务重试示例"""
    print("=" * 50)
    print("示例4: 任务重试机制")
    print("=" * 50)
    
    result = task_with_retry.delay("test_value")
    print(f"任务已提交，ID: {result.id}")
    
    try:
        final_result = result.get(timeout=30)
        print(f"任务最终结果: {final_result}\n")
    except Exception as e:
        print(f"任务最终失败: {e}\n")


def example_custom_retry():
    """自定义重试逻辑示例"""
    print("=" * 50)
    print("示例5: 自定义重试策略")
    print("=" * 50)
    
    result = task_with_custom_retry.delay("https://example.com/api")
    print(f"任务已提交，ID: {result.id}")
    
    try:
        final_result = result.get(timeout=60)
        print(f"任务最终结果: {final_result}\n")
    except Exception as e:
        print(f"任务最终失败: {e}\n")


def example_complex_workflow():
    """复杂工作流示例"""
    print("=" * 50)
    print("示例6: 复杂工作流（链 + 组）")
    print("=" * 50)
    
    # 先获取数据，然后并行处理，最后保存
    workflow = chain(
        fetch_data.s('main_source'),
        # 对获取的数据进行并行处理
        group(
            process_item.s(),
            process_item.s(),
            process_item.s(),
        ),
        # 聚合结果
        aggregate_results.s(),
    )
    
    result = workflow.apply_async()
    print(f"复杂工作流已提交")
    print(f"最终结果: {result.get(timeout=60)}\n")


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Celery 高级用法示例")
    print("=" * 50 + "\n")
    
    # 运行示例
    example_task_chain()
    example_task_group()
    example_chord()
    example_task_retry()
    example_custom_retry()
    example_complex_workflow()
    
    print("所有高级示例执行完成！")

