#!/usr/bin/env python3
"""
消息队列实时监控工具

实时显示 Redis 队列的变化，包括：
- 队列长度
- 任务状态
- Worker 状态
- 任务执行情况
"""

import sys
from pathlib import Path
import time
import os

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import redis
    from celery_app import app
    from celery.result import AsyncResult
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("💡 请先安装依赖: pip install celery redis")
    sys.exit(1)


class QueueMonitor:
    """队列监控器"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, redis_password=None):
        """初始化监控器"""
        try:
            if redis_password:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True
                )
            else:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
            
            # 测试连接
            self.redis_client.ping()
            print("✅ Redis 连接成功")
        except Exception as e:
            print(f"❌ Redis 连接失败: {e}")
            sys.exit(1)
    
    def get_queue_length(self, queue_name='celery'):
        """获取队列长度"""
        try:
            return self.redis_client.llen(queue_name)
        except:
            return 0
    
    def get_all_queues(self):
        """获取所有队列信息"""
        queues = {}
        
        # 获取配置的队列
        task_routes = app.conf.get('task_routes', {})
        queue_names = set()
        for route in task_routes.values():
            if 'queue' in route:
                queue_names.add(route['queue'])
        
        # 添加默认队列
        queue_names.add('celery')
        
        for queue_name in queue_names:
            length = self.get_queue_length(queue_name)
            queues[queue_name] = length
        
        return queues
    
    def get_queue_items(self, queue_name='celery', limit=10):
        """获取队列中的任务（不删除）"""
        try:
            items = self.redis_client.lrange(queue_name, 0, limit - 1)
            return items
        except:
            return []
    
    def get_active_tasks(self):
        """获取正在执行的任务"""
        try:
            inspect = app.control.inspect()
            active = inspect.active()
            return active or {}
        except:
            return {}
    
    def get_reserved_tasks(self):
        """获取已保留的任务（Worker 已获取但未执行）"""
        try:
            inspect = app.control.inspect()
            reserved = inspect.reserved()
            return reserved or {}
        except:
            return {}
    
    def get_scheduled_tasks(self):
        """获取计划执行的任务"""
        try:
            inspect = app.control.inspect()
            scheduled = inspect.scheduled()
            return scheduled or {}
        except:
            return {}
    
    def get_worker_stats(self):
        """获取 Worker 统计信息"""
        try:
            inspect = app.control.inspect()
            stats = inspect.stats()
            return stats or {}
        except:
            return {}
    
    def get_registered_tasks(self):
        """获取已注册的任务"""
        try:
            inspect = app.control.inspect()
            registered = inspect.registered()
            return registered or {}
        except:
            return {}
    
    def format_task_info(self, task_data):
        """格式化任务信息"""
        if not task_data:
            return "无"
        
        info = []
        for worker, tasks in task_data.items():
            info.append(f"  {worker}: {len(tasks)} 个任务")
            for task in tasks[:3]:  # 只显示前3个
                task_name = task.get('name', 'unknown')
                task_id = task.get('id', 'unknown')
                info.append(f"    - {task_name} (ID: {task_id[:8]}...)")
            if len(tasks) > 3:
                info.append(f"    ... 还有 {len(tasks) - 3} 个任务")
        
        return "\n".join(info) if info else "无"
    
    def monitor(self, interval=2, show_details=False):
        """实时监控队列"""
        print("\n" + "=" * 80)
        print("📊 Celery 消息队列实时监控")
        print("=" * 80)
        print(f"刷新间隔: {interval} 秒")
        print("按 Ctrl+C 退出")
        print("=" * 80 + "\n")
        
        try:
            while True:
                # 清屏（可选）
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Unix/Linux/macOS
                    os.system('clear')
                
                print("\n" + "=" * 80)
                print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 80)
                
                # 1. 队列信息
                print("\n📦 队列信息:")
                print("-" * 80)
                queues = self.get_all_queues()
                total_queued = 0
                for queue_name, length in queues.items():
                    total_queued += length
                    status = "🟢" if length > 0 else "⚪"
                    print(f"  {status} {queue_name:20s}: {length:4d} 个任务")
                print(f"  总计: {total_queued} 个任务在队列中")
                
                # 2. Worker 状态
                print("\n👷 Worker 状态:")
                print("-" * 80)
                worker_stats = self.get_worker_stats()
                if worker_stats:
                    for worker, stats in worker_stats.items():
                        pool = stats.get('pool', {})
                        pool_size = pool.get('max-concurrency', 'N/A')
                        total = stats.get('total', {})
                        succeeded = total.get('tasks.succeeded', 0)
                        failed = total.get('tasks.failed', 0)
                        print(f"  {worker}")
                        print(f"    池大小: {pool_size}")
                        print(f"    成功: {succeeded}, 失败: {failed}")
                else:
                    print("  ⚠️  未检测到活跃的 Workers")
                    print("  💡 提示: 请启动 Worker: celery -A celery_app worker --loglevel=info")
                
                # 3. 正在执行的任务
                print("\n🔄 正在执行的任务:")
                print("-" * 80)
                active_tasks = self.get_active_tasks()
                if active_tasks:
                    for worker, tasks in active_tasks.items():
                        print(f"  {worker}: {len(tasks)} 个任务")
                        for task in tasks:
                            task_name = task.get('name', 'unknown')
                            task_id = task.get('id', 'unknown')
                            args = task.get('args', [])
                            print(f"    - {task_name} (ID: {task_id[:16]}...)")
                            if show_details and args:
                                print(f"      参数: {args}")
                else:
                    print("  无")
                
                # 4. 已保留的任务（Worker 已获取但未执行）
                print("\n📋 已保留的任务（Worker 已获取但未执行）:")
                print("-" * 80)
                reserved_tasks = self.get_reserved_tasks()
                if reserved_tasks:
                    total_reserved = sum(len(tasks) for tasks in reserved_tasks.values())
                    print(f"  总计: {total_reserved} 个任务")
                    for worker, tasks in reserved_tasks.items():
                        if tasks:
                            print(f"  {worker}: {len(tasks)} 个任务")
                else:
                    print("  无")
                
                # 5. 计划执行的任务
                print("\n⏰ 计划执行的任务:")
                print("-" * 80)
                scheduled_tasks = self.get_scheduled_tasks()
                if scheduled_tasks:
                    total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())
                    print(f"  总计: {total_scheduled} 个任务")
                    for worker, tasks in scheduled_tasks.items():
                        if tasks:
                            print(f"  {worker}: {len(tasks)} 个任务")
                else:
                    print("  无")
                
                # 6. 已注册的任务
                if show_details:
                    print("\n📝 已注册的任务:")
                    print("-" * 80)
                    registered = self.get_registered_tasks()
                    if registered:
                        for worker, tasks in registered.items():
                            print(f"  {worker}: {len(tasks)} 个任务类型")
                            if tasks:
                                print(f"    示例: {', '.join(tasks[:5])}")
                                if len(tasks) > 5:
                                    print(f"    ... 还有 {len(tasks) - 5} 个任务类型")
                    else:
                        print("  无")
                
                print("\n" + "=" * 80)
                print(f"下次刷新: {interval} 秒后 (按 Ctrl+C 退出)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Celery 消息队列实时监控工具')
    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=2.0,
        help='刷新间隔（秒），默认 2.0'
    )
    parser.add_argument(
        '--details', '-d',
        action='store_true',
        help='显示详细信息（包括已注册的任务）'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Redis 主机地址，默认 localhost'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=6379,
        help='Redis 端口，默认 6379'
    )
    parser.add_argument(
        '--db',
        type=int,
        default=0,
        help='Redis 数据库编号，默认 0'
    )
    parser.add_argument(
        '--password',
        default=None,
        help='Redis 密码（如果需要）'
    )
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = QueueMonitor(
        redis_host=args.host,
        redis_port=args.port,
        redis_db=args.db,
        redis_password=args.password
    )
    
    # 开始监控
    monitor.monitor(interval=args.interval, show_details=args.details)


if __name__ == '__main__':
    main()

