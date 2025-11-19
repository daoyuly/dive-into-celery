"""
Worker 架构演示

这个脚本演示了任务和 Worker 的关系，以及超时机制的工作原理
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import os
from celery_app import app
from tasks.basic_tasks import add, long_running_task
from celery.result import AsyncResult


def demonstrate_task_worker_relationship():
    """演示任务和 Worker 的关系"""
    print("=" * 60)
    print("演示 1: 任务和 Worker 的关系")
    print("=" * 60)
    
    print("\n1. 任务定义（只是代码，不会执行）")
    print("   @app.task")
    print("   def add(x, y):")
    print("       return x + y")
    
    print("\n2. 提交任务到消息队列")
    result = add.delay(4, 5)
    print(f"   任务ID: {result.id}")
    print(f"   任务状态: {result.state}")
    print("   ⚠️  注意: 此时任务还未执行！")
    
    print("\n3. Worker 从队列获取任务")
    print("   Worker 主进程 → 从 Redis 获取任务 → 分配给子进程")
    
    print("\n4. Worker 子进程执行任务")
    print("   子进程 → 反序列化消息 → 找到任务函数 → 执行")
    
    print("\n5. 等待任务完成...")
    value = result.get(timeout=10)
    print(f"   任务结果: {value}")
    print(f"   最终状态: {result.state}")
    
    print("\n✅ 关键理解:")
    print("   - 任务只是代码定义，存储在应用代码中")
    print("   - Worker 是独立进程，从队列获取任务并执行")
    print("   - 任务和 Worker 可以运行在不同的机器上")


def demonstrate_worker_processes():
    """演示 Worker 进程架构"""
    print("\n" + "=" * 60)
    print("演示 2: Worker 进程架构")
    print("=" * 60)
    
    print("\nWorker 架构:")
    print("┌─────────────────────────────────────┐")
    print("│  Worker 主进程（Manager）          │")
    print("│  ├── 子进程 1 (Worker-1)            │")
    print("│  ├── 子进程 2 (Worker-2)           │")
    print("│  ├── 子进程 3 (Worker-3)           │")
    print("│  └── 子进程 4 (Worker-4)           │")
    print("└─────────────────────────────────────┘")
    
    print("\n当前进程信息:")
    print(f"   进程ID (PID): {os.getpid()}")
    print(f"   父进程ID (PPID): {os.getppid()}")
    
    print("\n✅ 关键理解:")
    print("   - Worker 是进程，不是线程")
    print("   - 每个子进程有独立的内存空间")
    print("   - 一个任务崩溃不会影响其他任务")


def demonstrate_soft_timeout():
    """演示软超时机制"""
    print("\n" + "=" * 60)
    print("演示 3: 软超时机制")
    print("=" * 60)
    
    print("\n软超时 (task_soft_time_limit):")
    print("   - 触发 SoftTimeLimitExceeded 异常")
    print("   - 任务可以捕获异常并优雅退出")
    print("   - 进程不会终止")
    
    print("\n提交长时间运行的任务（带进度跟踪）...")
    result = long_running_task.delay(duration=3)  # 3秒任务
    
    print("\n监控任务执行:")
    while not result.ready():
        info = result.info
        if isinstance(info, dict):
            percent = info.get('percent', 0)
            current = info.get('current', 0)
            total = info.get('total', 0)
            print(f"   进度: {percent}% ({current}/{total})")
        time.sleep(0.5)
    
    print(f"\n任务完成: {result.get()}")
    
    print("\n✅ 关键理解:")
    print("   - 软超时不会终止进程")
    print("   - 任务可以捕获异常并清理资源")
    print("   - 适合需要清理资源的任务")


def demonstrate_hard_timeout():
    """演示硬超时机制"""
    print("\n" + "=" * 60)
    print("演示 4: 硬超时机制（理论说明）")
    print("=" * 60)
    
    print("\n硬超时 (task_time_limit):")
    print("   - Worker 主进程监控子进程执行时间")
    print("   - 如果超过硬超时，主进程发送 SIGKILL 信号")
    print("   - 子进程被强制终止，无法清理资源")
    
    print("\n硬超时工作原理:")
    print("┌─────────────────────────────────────┐")
    print("│  Worker 主进程（监控者）           │")
    print("│  ┌───────────────────────────────┐ │")
    print("│  │  定时器: 5分钟                │ │")
    print("│  │  如果超时 → SIGKILL 子进程   │ │")
    print("│  └───────────────────────────────┘ │")
    print("│           │                        │")
    print("│           │ 监控                    │")
    print("│           ▼                        │")
    print("│  ┌───────────────────────────────┐ │")
    print("│  │  Worker 子进程（执行任务）    │ │")
    print("│  │  my_task() 正在执行...       │ │")
    print("│  │  (已经执行了 5分01秒)        │ │")
    print("│  └───────────────────────────────┘ │")
    print("│           │                        │")
    print("│           │ SIGKILL (强制终止)     │")
    print("│           ▼                        │")
    print("│  ┌───────────────────────────────┐ │")
    print("│  │  子进程被强制终止             │ │")
    print("│  │  - 无法执行清理代码           │ │")
    print("│  │  - 无法保存状态                │ │")
    print("│  └───────────────────────────────┘ │")
    print("└─────────────────────────────────────┘")
    
    print("\n为什么不能只终止任务，而要终止进程？")
    print("   1. Python 的 GIL（全局解释器锁）")
    print("   2. 任务可能在阻塞操作中（无法中断）")
    print("   3. 任务可能陷入死循环（无法中断）")
    
    print("\n硬超时的影响:")
    print("   ✅ 任务停止执行（达到目的）")
    print("   ❌ 无法执行清理代码（finally 块不会执行）")
    print("   ❌ 无法保存中间状态")
    print("   ❌ 可能导致资源泄漏")
    print("   ❌ 可能导致数据不一致")
    
    print("\n✅ 最佳实践:")
    print("   - 使用软超时 + 硬超时组合")
    print("   - 软超时: 给任务机会优雅退出")
    print("   - 硬超时: 确保任务最终会被终止")


def demonstrate_best_practices():
    """演示最佳实践"""
    print("\n" + "=" * 60)
    print("演示 5: 超时处理最佳实践")
    print("=" * 60)
    
    print("\n1. 配置软超时 + 硬超时")
    print("   task_soft_time_limit=240  # 4分钟软超时")
    print("   task_time_limit=300        # 5分钟硬超时")
    
    print("\n2. 在任务中处理软超时")
    print("""
   from celery.exceptions import SoftTimeLimitExceeded
   
   @app.task(bind=True, soft_time_limit=240, time_limit=300)
   def my_task(self):
       try:
           # 任务逻辑
           process_data()
       except SoftTimeLimitExceeded:
           # 优雅处理超时
           save_checkpoint()
           cleanup()
           raise
   """)
    
    print("\n3. 定期检查超时")
    print("""
   @app.task(bind=True, soft_time_limit=240)
   def long_task(self):
       for i in range(1000000):
           if self.is_aborted():
               save_checkpoint()
               return "任务已中断"
           process_item(i)
   """)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Worker 架构和超时机制演示")
    print("=" * 60)
    
    try:
        demonstrate_task_worker_relationship()
        demonstrate_worker_processes()
        demonstrate_soft_timeout()
        demonstrate_hard_timeout()
        demonstrate_best_practices()
        
        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("   - 详细说明请查看: TASK_WORKER_RELATIONSHIP.md")
        print("   - 确保 Worker 正在运行: celery -A celery_app worker")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n💡 提示: 请确保 Redis 正在运行，并且 Celery Worker 已启动")

