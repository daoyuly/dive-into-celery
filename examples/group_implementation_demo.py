"""
Group 实现机制演示

这个脚本深入演示了 Celery Group 的内部工作机制，包括：
1. Group 的创建过程
2. Group ID 的设置
3. 并行执行机制
4. 结果收集机制
5. Group 与 Chain 的组合
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from celery import group, chain
import time
import json
import os


@app.task(name='tasks.group_demo.fetch_data')
def fetch_data(source):
    """获取数据任务"""
    print(f"[fetch_data] 从 {source} 获取数据...")
    print(f"[fetch_data] Worker PID: {os.getpid()}")
    time.sleep(2)  # 模拟耗时操作
    result = f"data_from_{source}"
    print(f"[fetch_data] 返回结果: {result}")
    return result


@app.task(name='tasks.group_demo.process_item')
def process_item(item):
    """处理单个项目"""
    print(f"[process_item] 处理: {item}")
    time.sleep(1)  # 模拟处理时间
    result = f"processed_{item}"
    print(f"[process_item] 返回结果: {result}")
    return result


@app.task(name='tasks.group_demo.aggregate')
def aggregate(results):
    """聚合结果"""
    print(f"[aggregate] 聚合 {len(results)} 个结果: {results}")
    return f"aggregated_{len(results)}_items"


def demonstrate_group_creation():
    """演示 Group 的创建过程"""
    print("=" * 70)
    print("演示1: Group 的创建过程")
    print("=" * 70)
    
    # 创建任务签名
    sig1 = fetch_data.s('source1')
    sig2 = fetch_data.s('source2')
    sig3 = fetch_data.s('source3')
    
    print("\n1. 创建任务签名:")
    print(f"   sig1: {sig1}")
    print(f"   sig2: {sig2}")
    print(f"   sig3: {sig3}")
    
    # 创建 Group
    job = group(sig1, sig2, sig3)
    
    print("\n2. 创建 Group:")
    print(f"   job: {job}")
    print(f"   job.tasks: {len(job.tasks)} 个任务")
    
    # 检查任务签名
    print("\n3. 检查任务签名:")
    for i, task in enumerate(job.tasks):
        print(f"   Task {i+1} ({task.task}):")
        print(f"      args: {task.args}")
        print(f"      kwargs: {task.kwargs}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_group_id():
    """演示 Group ID 的设置"""
    print("=" * 70)
    print("演示2: Group ID 的设置")
    print("=" * 70)
    
    job = group(
        fetch_data.s('source1'),
        fetch_data.s('source2'),
        fetch_data.s('source3')
    )
    
    print("\n提交 Group 前:")
    print("  任务还没有 group_id")
    
    print("\n提交 Group (apply_async):")
    result = job.apply_async()
    
    print(f"\nGroup ID: {result.id}")
    print(f"子任务数量: {len(result.results)}")
    
    print("\n每个子任务的 ID:")
    for i, async_result in enumerate(result.results):
        print(f"  任务 {i+1}: {async_result.id}")
    
    print("\n注意: 所有任务共享相同的 group_id（在消息中设置）")
    print("      group_id 用于结果收集和状态跟踪")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_parallel_execution():
    """演示并行执行机制"""
    print("=" * 70)
    print("演示3: 并行执行机制")
    print("=" * 70)
    
    print("\n创建 Group（3 个任务，每个需要 2 秒）:")
    job = group(
        fetch_data.s('source1'),
        fetch_data.s('source2'),
        fetch_data.s('source3')
    )
    
    print("\n执行 Group:")
    print("  如果串行执行，总时间 = 2 + 2 + 2 = 6 秒")
    print("  如果并行执行，总时间 ≈ 2 秒（最慢任务的时间）")
    
    start_time = time.time()
    result = job.apply_async()
    print(f"\n提交时间: {time.time() - start_time:.2f} 秒（立即返回）")
    
    print("\n等待所有任务完成...")
    try:
        results = result.get(timeout=30)
        elapsed_time = time.time() - start_time
        print(f"\n✅ 所有任务完成")
        print(f"   总执行时间: {elapsed_time:.2f} 秒")
        print(f"   结果: {results}")
        
        if elapsed_time < 3:
            print("\n   ✓ 任务并行执行（总时间接近单个任务时间）")
        else:
            print("\n   ⚠️  任务可能串行执行（总时间接近所有任务时间总和）")
            print("      可能原因：Worker 并发数不足")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_result_collection():
    """演示结果收集机制"""
    print("=" * 70)
    print("演示4: 结果收集机制")
    print("=" * 70)
    
    job = group(
        process_item.s('item1'),
        process_item.s('item2'),
        process_item.s('item3')
    )
    
    print("\n提交 Group...")
    result = job.apply_async()
    
    print("\n结果收集方式:")
    print("  1. 获取所有结果: result.get()")
    print("  2. 获取单个任务结果: result.results[0].get()")
    print("  3. 检查状态: result.ready(), result.successful()")
    
    print("\n等待结果...")
    try:
        # 方式1: 获取所有结果
        all_results = result.get(timeout=30)
        print(f"\n✅ 所有结果: {all_results}")
        
        # 方式2: 获取单个任务结果
        print(f"\n第一个任务的结果: {result.results[0].get()}")
        
        # 方式3: 检查状态
        print(f"\n状态检查:")
        print(f"  所有任务完成: {result.ready()}")
        print(f"  所有任务成功: {result.successful()}")
        print(f"  有任务失败: {result.failed()}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_result_order():
    """演示结果顺序"""
    print("=" * 70)
    print("演示5: 结果顺序")
    print("=" * 70)
    
    @app.task(name='tasks.group_demo.slow_task')
    def slow_task():
        print("[slow_task] 开始执行（需要 3 秒）")
        time.sleep(3)
        return "slow_result"
    
    @app.task(name='tasks.group_demo.fast_task')
    def fast_task():
        print("[fast_task] 开始执行（需要 1 秒）")
        time.sleep(1)
        return "fast_result"
    
    @app.task(name='tasks.group_demo.medium_task')
    def medium_task():
        print("[medium_task] 开始执行（需要 2 秒）")
        time.sleep(2)
        return "medium_result"
    
    print("\n创建 Group（任务执行时间不同）:")
    print("  slow_task: 3 秒")
    print("  fast_task: 1 秒")
    print("  medium_task: 2 秒")
    
    job = group(
        slow_task.s(),   # 最慢
        fast_task.s(),   # 最快
        medium_task.s()  # 中等
    )
    
    print("\n执行 Group...")
    result = job.apply_async()
    
    print("\n重要: Group 返回的结果列表保持任务定义的顺序，")
    print("      而不是任务完成的顺序！")
    
    try:
        results = result.get(timeout=30)
        print(f"\n结果列表: {results}")
        print(f"  results[0] = {results[0]} (slow_task，即使最后完成)")
        print(f"  results[1] = {results[1]} (fast_task，即使最先完成)")
        print(f"  results[2] = {results[2]} (medium_task)")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_error_handling():
    """演示错误处理"""
    print("=" * 70)
    print("演示6: 错误处理")
    print("=" * 70)
    
    @app.task(name='tasks.group_demo.success_task')
    def success_task(value):
        return f"success_{value}"
    
    @app.task(name='tasks.group_demo.fail_task')
    def fail_task(value):
        raise Exception(f"模拟失败: {value}")
    
    print("\n创建 Group（包含成功和失败的任务）:")
    job = group(
        success_task.s('task1'),
        fail_task.s('task2'),      # 会失败
        success_task.s('task3')
    )
    
    print("\n执行 Group...")
    result = job.apply_async()
    
    print("\n错误处理方式:")
    print("  1. propagate=True: 任何任务失败都会抛出异常")
    print("  2. propagate=False: 返回结果列表，失败的任务返回异常对象")
    
    # 方式1: propagate=True
    print("\n方式1: propagate=True")
    try:
        results = result.get(propagate=True, timeout=30)
        print(f"  结果: {results}")
    except Exception as e:
        print(f"  ❌ 捕获异常: {e}")
    
    # 方式2: propagate=False
    print("\n方式2: propagate=False")
    try:
        results = result.get(propagate=False, timeout=30)
        print(f"  结果: {results}")
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"    任务 {i+1} 失败: {r}")
            else:
                print(f"    任务 {i+1} 成功: {r}")
    except Exception as e:
        print(f"  ❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_group_with_chain():
    """演示 Group 与 Chain 的组合"""
    print("=" * 70)
    print("演示7: Group 与 Chain 的组合")
    print("=" * 70)
    
    @app.task(name='tasks.group_demo.fetch_main_data')
    def fetch_main_data(source):
        print(f"[fetch_main_data] 从 {source} 获取数据")
        data = ['item1', 'item2', 'item3']
        print(f"[fetch_main_data] 返回: {data}")
        return data
    
    print("\n工作流:")
    print("  1. fetch_main_data('source') → 返回数据列表")
    print("  2. 并行处理列表中的每个项目 (Group)")
    print("  3. aggregate(所有处理结果) → 最终结果")
    
    workflow = chain(
        fetch_main_data.s('source'),
        group(
            process_item.s(),
            process_item.s(),
            process_item.s(),
        ),
        aggregate.s()
    )
    
    print("\n提交复杂工作流...")
    result = workflow.apply_async()
    
    try:
        final_result = result.get(timeout=60)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_dynamic_group():
    """演示动态 Group 创建"""
    print("=" * 70)
    print("演示8: 动态 Group 创建")
    print("=" * 70)
    
    print("\n方式1: 使用列表推导式")
    print("  job = group(process_item.s(i) for i in range(10))")
    
    # 创建较小的 Group 用于演示
    job = group(
        process_item.s(f'item_{i}') for i in range(5)
    )
    
    print(f"\n创建的 Group 包含 {len(job.tasks)} 个任务")
    
    print("\n提交 Group...")
    result = job.apply_async()
    
    try:
        results = result.get(timeout=30)
        print(f"\n✅ 所有结果: {results}")
        print(f"   结果数量: {len(results)}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Celery Group 实现机制深度演示")
    print("=" * 70 + "\n")
    
    # 运行演示
    demonstrate_group_creation()
    
    print("\n⚠️  注意: 以下演示需要 Worker 正在运行")
    print("   请确保已启动 Worker: celery -A celery_app worker --loglevel=info\n")
    
    input("按 Enter 键继续 Group ID 演示...")
    demonstrate_group_id()
    
    input("按 Enter 键继续并行执行演示...")
    demonstrate_parallel_execution()
    
    input("按 Enter 键继续结果收集演示...")
    demonstrate_result_collection()
    
    input("按 Enter 键继续结果顺序演示...")
    demonstrate_result_order()
    
    input("按 Enter 键继续错误处理演示...")
    demonstrate_error_handling()
    
    input("按 Enter 键继续 Group 与 Chain 组合演示...")
    demonstrate_group_with_chain()
    
    input("按 Enter 键继续动态 Group 创建演示...")
    demonstrate_dynamic_group()
    
    print("\n" + "=" * 70)
    print("所有演示完成！")
    print("=" * 70 + "\n")
    print("详细分析请参考: doc/GROUP_IMPLEMENTATION_DEEP_DIVE.md")

