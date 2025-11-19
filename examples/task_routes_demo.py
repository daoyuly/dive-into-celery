"""
Task Routes 演示

演示 task_routes 的作用和工作机制
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from tasks.basic_tasks import add, multiply
from tasks.advanced_tasks import fetch_data
from tasks.realworld_tasks import send_email
import time


def demonstrate_routing_config():
    """演示路由配置"""
    print("=" * 60)
    print("演示 1: 查看路由配置")
    print("=" * 60)
    
    print("\n当前路由配置:")
    print("-" * 60)
    task_routes = app.conf.task_routes
    for pattern, route in task_routes.items():
        queue = route.get('queue', 'default')
        priority = route.get('priority', 'default')
        print(f"  模式: {pattern}")
        print(f"    队列: {queue}")
        if priority != 'default':
            print(f"    优先级: {priority}")
        print()


def demonstrate_task_routing():
    """演示任务路由"""
    print("=" * 60)
    print("演示 2: 任务路由过程")
    print("=" * 60)
    
    # 测试不同任务的路由
    test_tasks = [
        ('tasks.basic_tasks.add', add),
        ('tasks.advanced_tasks.fetch_data', fetch_data),
        ('tasks.realworld_tasks.send_email', send_email),
    ]
    
    print("\n任务路由测试:")
    print("-" * 60)
    
    for task_name, task_func in test_tasks:
        # 获取路由配置
        route = None
        for pattern, route_config in app.conf.task_routes.items():
            # 简单的通配符匹配
            if pattern.endswith('*'):
                prefix = pattern[:-1]  # 移除 *
                if task_name.startswith(prefix):
                    route = route_config
                    break
            elif pattern == task_name:
                route = route_config
                break
        
        if route:
            queue = route.get('queue', 'default')
            print(f"  {task_name}")
            print(f"    → 路由到队列: {queue}")
        else:
            print(f"  {task_name}")
            print(f"    → 使用默认队列")
        print()


def demonstrate_queue_isolation():
    """演示队列隔离"""
    print("=" * 60)
    print("演示 3: 队列隔离效果")
    print("=" * 60)
    
    print("\n提交任务到不同队列:")
    print("-" * 60)
    
    # 提交基础任务
    result1 = add.delay(4, 5)
    print(f"  基础任务 (add): ID={result1.id[:16]}...")
    print(f"    应该路由到: basic 队列")
    
    # 提交高级任务
    result2 = fetch_data.delay('source1')
    print(f"  高级任务 (fetch_data): ID={result2.id[:16]}...")
    print(f"    应该路由到: advanced 队列")
    
    # 提交实际工程任务
    result3 = send_email.delay(
        to_email='test@example.com',
        subject='Test',
        body='Test body'
    )
    print(f"  实际工程任务 (send_email): ID={result3.id[:16]}...")
    print(f"    应该路由到: realworld 队列")
    
    print("\n💡 提示:")
    print("  - 使用 queue_monitor.py 查看队列变化")
    print("  - 使用 redis_queue_viewer.py 查看队列内容")
    print("  - 确保 Worker 监听相应的队列")


def demonstrate_priority_routing():
    """演示优先级路由"""
    print("=" * 60)
    print("演示 4: 优先级路由（理论说明）")
    print("=" * 60)
    
    print("\n优先级路由配置示例:")
    print("-" * 60)
    print("""
  task_routes={
      'tasks.critical.*': {
          'queue': 'critical',
          'priority': 9,  # 高优先级
      },
      'tasks.normal.*': {
          'queue': 'normal',
          'priority': 5,  # 普通优先级
      },
      'tasks.background.*': {
          'queue': 'background',
          'priority': 1,  # 低优先级
      },
  }
    """)
    
    print("优先级说明:")
    print("  - 范围: 0-9（数字越大优先级越高）")
    print("  - 高优先级任务会优先执行")
    print("  - 需要 Worker 支持优先级队列")


def demonstrate_worker_queue_matching():
    """演示 Worker 和队列的匹配"""
    print("=" * 60)
    print("演示 5: Worker 和队列匹配")
    print("=" * 60)
    
    print("\nWorker 启动命令示例:")
    print("-" * 60)
    print("""
  # 只处理基础任务队列
  celery -A celery_app worker --queues=basic
  
  # 处理多个队列
  celery -A celery_app worker --queues=basic,advanced,realworld
  
  # 处理所有队列
  celery -A celery_app worker --queues=basic,advanced,realworld
    """)
    
    print("\n匹配规则:")
    print("  - Worker 只处理它监听的队列中的任务")
    print("  - 如果任务路由到 Worker 未监听的队列，任务会积压")
    print("  - 确保 Worker 监听所有需要的队列")


def demonstrate_dynamic_routing():
    """演示动态路由"""
    print("=" * 60)
    print("演示 6: 动态路由（理论说明）")
    print("=" * 60)
    
    print("\n使用函数进行动态路由:")
    print("-" * 60)
    print("""
  def route_task(name, args, kwargs, options, task=None, **kw):
      \"\"\"动态路由函数\"\"\"
      if 'email' in name:
          return {'queue': 'email'}
      elif 'image' in name:
          return {'queue': 'image'}
      elif 'critical' in name:
          return {'queue': 'critical', 'priority': 9}
      else:
          return {'queue': 'default'}
  
  app.conf.task_routes = route_task
    """)
    
    print("动态路由的优势:")
    print("  - 可以根据任务名称动态决定路由")
    print("  - 可以根据任务参数决定路由")
    print("  - 可以实现复杂的路由逻辑")


def demonstrate_routing_debugging():
    """演示路由调试"""
    print("=" * 60)
    print("演示 7: 路由调试方法")
    print("=" * 60)
    
    print("\n调试方法:")
    print("-" * 60)
    
    print("\n1. 查看路由配置:")
    print("  from celery_app import app")
    print("  print(app.conf.task_routes)")
    
    print("\n2. 查看任务名称:")
    print("  print(task.name)")
    
    print("\n3. 查看队列内容:")
    print("  python3 redis_queue_viewer.py")
    
    print("\n4. 查看 Worker 状态:")
    print("  python3 queue_monitor.py")
    
    print("\n5. 检查 Worker 监听的队列:")
    print("  from celery_app import app")
    print("  inspect = app.control.inspect()")
    print("  active_queues = inspect.active_queues()")
    print("  print(active_queues)")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Task Routes 工作机制演示")
    print("=" * 60)
    
    try:
        demonstrate_routing_config()
        demonstrate_task_routing()
        demonstrate_queue_isolation()
        demonstrate_priority_routing()
        demonstrate_worker_queue_matching()
        demonstrate_dynamic_routing()
        demonstrate_routing_debugging()
        
        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("  - 详细说明请查看: TASK_ROUTES_DEEP_DIVE.md")
        print("  - 使用 queue_monitor.py 查看队列变化")
        print("  - 确保 Worker 正在运行并监听相应队列")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 提示: 请确保 Redis 正在运行，并且 Celery Worker 已启动")

