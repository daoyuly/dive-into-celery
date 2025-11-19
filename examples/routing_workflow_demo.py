"""
路由工作流程演示

可视化展示 task_routes 的工作流程
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from tasks.basic_tasks import add
import time


def visualize_routing_workflow():
    """可视化路由工作流程"""
    print("\n" + "=" * 80)
    print("Task Routes 工作流程可视化")
    print("=" * 80)
    
    print("\n步骤 1: 任务定义")
    print("-" * 80)
    print("""
  @app.task
  def add(x, y):
      return x + y
    """)
    
    print("\n步骤 2: 任务提交")
    print("-" * 80)
    print("""
  result = add.delay(4, 5)
    """)
    
    print("\n步骤 3: Celery 查找路由配置")
    print("-" * 80)
    print("  检查 app.conf.task_routes:")
    task_routes = app.conf.task_routes
    for pattern, route in task_routes.items():
        queue = route.get('queue', 'default')
        print(f"    {pattern} → {queue}")
    
    print("\n步骤 4: 匹配任务名称")
    print("-" * 80)
    task_name = 'tasks.basic_tasks.add'
    print(f"  任务名称: {task_name}")
    
    matched_route = None
    for pattern, route_config in task_routes.items():
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            if task_name.startswith(prefix):
                matched_route = route_config
                print(f"  匹配规则: {pattern}")
                break
    
    if matched_route:
        queue = matched_route.get('queue', 'default')
        print(f"  匹配结果: 路由到队列 '{queue}'")
    else:
        print("  匹配结果: 使用默认队列")
    
    print("\n步骤 5: 发送到指定队列")
    print("-" * 80)
    if matched_route:
        queue = matched_route.get('queue', 'default')
        print(f"  任务消息发送到 Redis 队列: {queue}")
        print(f"  Redis 命令: LPUSH {queue} <task_message>")
    
    print("\n步骤 6: Worker 从队列获取任务")
    print("-" * 80)
    print("""
  Worker 主进程 → 从 Redis 队列获取任务 → 分配给子进程执行
  
  Worker 必须监听相应的队列:
  celery -A celery_app worker --queues=basic,advanced,realworld
    """)
    
    print("\n完整流程图:")
    print("-" * 80)
    print("""
  ┌─────────────────┐
  │  任务提交       │
  │  add.delay(4,5) │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  查找路由配置   │
  │  task_routes    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  匹配任务名称   │
  │  'tasks.basic_  │
  │   tasks.add'    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  应用路由规则   │
  │  {'queue':      │
  │   'basic'}      │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  发送到队列      │
  │  Redis: basic   │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Worker 获取    │
  │  并执行任务      │
  └─────────────────┘
    """)


def demonstrate_actual_routing():
    """演示实际路由过程"""
    print("\n" + "=" * 80)
    print("实际路由演示")
    print("=" * 80)
    
    print("\n提交任务并观察路由:")
    print("-" * 80)
    
    # 提交任务
    result = add.delay(4, 5)
    task_id = result.id
    
    print(f"  任务已提交")
    print(f"  任务ID: {task_id}")
    print(f"  任务名称: tasks.basic_tasks.add")
    print(f"  预期队列: basic")
    
    print("\n💡 提示:")
    print("  - 使用 queue_monitor.py 查看任务是否进入 basic 队列")
    print("  - 使用 redis_queue_viewer.py 查看队列内容")
    print("  - 确保 Worker 监听 basic 队列")
    
    # 等待任务完成
    try:
        value = result.get(timeout=10)
        print(f"\n  任务完成，结果: {value}")
    except Exception as e:
        print(f"\n  ⚠️  任务未完成: {e}")
        print("  💡 提示: 请确保 Worker 正在运行")


if __name__ == '__main__':
    try:
        visualize_routing_workflow()
        demonstrate_actual_routing()
        
        print("\n" + "=" * 80)
        print("✅ 路由工作流程演示完成！")
        print("=" * 80)
        print("\n💡 更多信息:")
        print("  - 详细说明: TASK_ROUTES_DEEP_DIVE.md")
        print("  - 路由演示: python3 examples/task_routes_demo.py")
        print("  - 队列监控: python3 queue_monitor.py")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

