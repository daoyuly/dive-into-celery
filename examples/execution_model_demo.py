"""
Celery 执行模型演示

演示 Celery 的不同执行模型（多进程、协程等）
"""

import sys
from pathlib import Path
import os
import time

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from tasks.basic_tasks import add, multiply


def demonstrate_execution_models():
    """演示不同的执行模型"""
    print("=" * 80)
    print("Celery 执行模型说明")
    print("=" * 80)
    
    print("\n❓ 问题: 任务在 Celery 中是以多线程执行的吗？")
    print("✅ 答案: 不是！Celery 默认使用多进程（Prefork），不是多线程")
    
    print("\n" + "=" * 80)
    print("执行模型对比")
    print("=" * 80)
    
    print("\n1. Prefork（多进程）- 默认模式")
    print("-" * 80)
    print("""
  特点:
    ✅ 使用多进程，每个任务在独立进程中执行
    ✅ 进程隔离，一个任务崩溃不影响其他任务
    ✅ 充分利用多核 CPU
    ✅ 适合 CPU 密集型任务
    ❌ 内存占用较大
    
  架构:
    Worker 主进程（Manager）
    ├── 子进程 1 (Worker-1) ← 独立进程，独立内存
    ├── 子进程 2 (Worker-2) ← 独立进程，独立内存
    ├── 子进程 3 (Worker-3) ← 独立进程，独立内存
    └── 子进程 4 (Worker-4) ← 独立进程，独立内存
    
  启动方式:
    celery -A celery_app worker --pool=prefork --concurrency=4
    """)
    
    print("\n2. Eventlet/Gevent（协程）- I/O 密集型")
    print("-" * 80)
    print("""
  特点:
    ✅ 使用协程（轻量级线程）
    ✅ 适合 I/O 密集型任务（网络请求、文件操作）
    ✅ 可以处理大量并发连接
    ✅ 内存占用较小
    ❌ 不适合 CPU 密集型任务（受 GIL 限制）
    
  架构:
    Worker 主进程
    └── 协程池
        ├── 协程 1 (执行任务 1)
        ├── 协程 2 (执行任务 2)
        ├── 协程 3 (执行任务 3)
        └── 协程 N (执行任务 N)
        （所有协程在同一个进程中）
    
  启动方式:
    pip install eventlet
    celery -A celery_app worker --pool=eventlet --concurrency=100
    """)
    
    print("\n3. Solo（单线程）- 仅用于调试")
    print("-" * 80)
    print("""
  特点:
    ✅ 单线程执行，易于调试
    ✅ 内存占用最小
    ❌ 无法并发执行任务
    ❌ 性能最差
    
  启动方式:
    celery -A celery_app worker --pool=solo
    """)


def demonstrate_why_multiprocess():
    """演示为什么使用多进程而不是多线程"""
    print("\n" + "=" * 80)
    print("为什么使用多进程而不是多线程？")
    print("=" * 80)
    
    print("\n1. Python 的 GIL（全局解释器锁）")
    print("-" * 80)
    print("""
  GIL 的限制:
    - Python 的 GIL 确保同一时刻只有一个线程执行 Python 字节码
    - 多线程在 CPU 密集型任务中无法真正并行执行
    - 多进程可以绕过 GIL，真正利用多核 CPU
    
  示例:
    # 多线程（受 GIL 限制）
    import threading
    # 4 个线程执行，但受 GIL 限制，实际上串行执行
    # 总时间 ≈ 单线程时间 × 4（没有并行加速）
    
    # 多进程（绕过 GIL）
    from multiprocessing import Process
    # 4 个进程执行，真正并行
    # 总时间 ≈ 单进程时间 / 4（真正的并行加速）
    """)
    
    print("\n2. 进程隔离的优势")
    print("-" * 80)
    print("""
  多进程的优势:
    ✅ 进程隔离：一个任务崩溃不会影响其他任务
    ✅ 内存隔离：每个进程有独立的内存空间
    ✅ 安全性：任务之间不会相互干扰
    
  多线程的问题:
    ❌ 共享内存：一个线程的错误可能影响其他线程
    ❌ 线程安全问题：需要加锁保护共享资源
    ❌ 调试困难：线程间交互复杂
    """)
    
    print("\n3. 实际性能对比")
    print("-" * 80)
    print("""
  CPU 密集型任务:
    多进程（Prefork）: ✅ 最佳性能，充分利用多核
    多线程:          ❌ 受 GIL 限制，性能差
    协程（Eventlet）: ❌ 受 GIL 限制，性能差
    
  I/O 密集型任务:
    协程（Eventlet/Gevent）: ✅ 最佳性能，高并发
    多进程（Prefork）:        ⚠️  性能好，但内存占用大
    多线程:                  ⚠️  性能一般，受 GIL 限制
    """)


def demonstrate_current_config():
    """演示当前配置"""
    print("\n" + "=" * 80)
    print("当前 Celery 配置")
    print("=" * 80)
    
    print("\nWorker 池类型:")
    print("-" * 80)
    pool = app.conf.get('worker_pool', 'prefork')
    print(f"  当前配置: {pool} (默认: prefork)")
    
    print("\n并发数:")
    print("-" * 80)
    concurrency = app.conf.get('worker_concurrency', 'auto')
    print(f"  当前配置: {concurrency} (默认: CPU 核心数)")
    
    print("\n预取数:")
    print("-" * 80)
    prefetch = app.conf.get('worker_prefetch_multiplier', 4)
    print(f"  当前配置: {prefetch}")
    
    print("\n💡 提示:")
    print("  - 默认使用 Prefork（多进程）")
    print("  - 并发数默认等于 CPU 核心数")
    print("  - 可以通过启动参数覆盖配置")


def demonstrate_process_info():
    """演示进程信息"""
    print("\n" + "=" * 80)
    print("当前进程信息")
    print("=" * 80)
    
    print("\n进程信息:")
    print("-" * 80)
    print(f"  进程ID (PID): {os.getpid()}")
    print(f"  父进程ID (PPID): {os.getppid()}")
    print(f"  进程名称: {os.path.basename(__file__)}")
    
    print("\n💡 说明:")
    print("  - 当前运行的是客户端进程（提交任务）")
    print("  - Worker 进程是独立的进程，运行在不同的进程中")
    print("  - 每个 Worker 子进程有独立的 PID")


def demonstrate_task_execution():
    """演示任务执行"""
    print("\n" + "=" * 80)
    print("任务执行演示")
    print("=" * 80)
    
    print("\n提交任务:")
    print("-" * 80)
    
    # 提交任务
    result1 = add.delay(4, 5)
    result2 = multiply.delay(6, 7)
    
    print(f"  任务1 (add): ID={result1.id[:16]}...")
    print(f"  任务2 (multiply): ID={result2.id[:16]}...")
    
    print("\n任务执行位置:")
    print("-" * 80)
    print("  - 任务在 Worker 子进程中执行（不是当前进程）")
    print("  - 每个任务在独立的 Worker 子进程中执行")
    print("  - Worker 进程可以运行在不同的机器上")
    
    print("\n等待任务完成...")
    try:
        value1 = result1.get(timeout=10)
        value2 = result2.get(timeout=10)
        print(f"  任务1 结果: {value1}")
        print(f"  任务2 结果: {value2}")
    except Exception as e:
        print(f"  ⚠️  任务未完成: {e}")
        print("  💡 提示: 请确保 Worker 正在运行")


def demonstrate_how_to_choose():
    """演示如何选择合适的执行模型"""
    print("\n" + "=" * 80)
    print("如何选择合适的执行模型？")
    print("=" * 80)
    
    print("\n决策树:")
    print("-" * 80)
    print("""
  任务类型？
  │
  ├─ CPU 密集型（计算、图像处理）
  │  └─→ Prefork（多进程）
  │      --pool=prefork --concurrency=CPU核心数
  │
  ├─ I/O 密集型（网络请求、文件操作）
  │  └─→ Eventlet/Gevent（协程）
  │      --pool=eventlet --concurrency=100-1000
  │
  └─ 调试/开发
     └─→ Solo（单线程）
         --pool=solo
    """)
    
    print("\n配置示例:")
    print("-" * 80)
    print("""
  # CPU 密集型任务
  celery -A celery_app worker --pool=prefork --concurrency=4
  
  # I/O 密集型任务
  pip install eventlet
  celery -A celery_app worker --pool=eventlet --concurrency=100
  
  # 混合场景（启动多个 Worker）
  celery -A celery_app worker --pool=prefork --concurrency=4 --queues=cpu
  celery -A celery_app worker --pool=eventlet --concurrency=100 --queues=io
    """)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Celery 执行模型演示")
    print("=" * 80)
    
    try:
        demonstrate_execution_models()
        demonstrate_why_multiprocess()
        demonstrate_current_config()
        demonstrate_process_info()
        demonstrate_task_execution()
        demonstrate_how_to_choose()
        
        print("\n" + "=" * 80)
        print("✅ 所有演示完成！")
        print("=" * 80)
        print("\n💡 关键要点:")
        print("  1. Celery 默认使用多进程（Prefork），不是多线程")
        print("  2. 多进程可以绕过 Python 的 GIL，真正利用多核 CPU")
        print("  3. 对于 I/O 密集型任务，可以使用协程（Eventlet/Gevent）")
        print("  4. 详细说明请查看: CELERY_EXECUTION_MODEL.md")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

