#!/usr/bin/env python3
"""
Redis 队列查看器

直接查看 Redis 中的队列内容，不依赖 Celery
"""

import sys
from pathlib import Path
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import redis
except ImportError:
    print("❌ 请先安装 redis: pip install redis")
    sys.exit(1)


def view_redis_queues(host='localhost', port=6379, db=0, password=None):
    """查看 Redis 队列内容"""
    try:
        if password:
            r = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        else:
            r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
        # 测试连接
        r.ping()
        print("✅ Redis 连接成功\n")
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return
    
    print("=" * 80)
    print("📦 Redis 队列内容查看")
    print("=" * 80)
    
    # 1. 查看所有键
    print("\n🔑 Redis 键列表（与 Celery 相关）:")
    print("-" * 80)
    all_keys = r.keys('*')
    celery_keys = [key for key in all_keys if 'celery' in key.lower() or 'task' in key.lower()]
    
    if celery_keys:
        for key in sorted(celery_keys)[:20]:  # 只显示前20个
            key_type = r.type(key)
            print(f"  {key_type:8s} {key}")
        if len(celery_keys) > 20:
            print(f"  ... 还有 {len(celery_keys) - 20} 个键")
    else:
        print("  未找到 Celery 相关的键")
    
    # 2. 查看队列（List 类型）
    print("\n📋 队列内容（List 类型）:")
    print("-" * 80)
    
    # 常见的队列名称
    queue_names = ['celery', 'basic', 'advanced', 'realworld']
    
    for queue_name in queue_names:
        length = r.llen(queue_name)
        if length > 0:
            print(f"\n  📦 队列: {queue_name} (长度: {length})")
            print("  " + "-" * 76)
            
            # 获取队列中的任务（不删除）
            items = r.lrange(queue_name, 0, 9)  # 只显示前10个
            
            for i, item in enumerate(items, 1):
                try:
                    # 尝试解析 JSON
                    task_data = json.loads(item)
                    task_name = task_data.get('task', 'unknown')
                    task_id = task_data.get('id', 'unknown')
                    args = task_data.get('args', [])
                    kwargs = task_data.get('kwargs', {})
                    
                    print(f"  [{i}] 任务: {task_name}")
                    print(f"      ID: {task_id}")
                    if args:
                        print(f"      参数: {args}")
                    if kwargs:
                        print(f"      关键字参数: {kwargs}")
                    print()
                except json.JSONDecodeError:
                    print(f"  [{i}] {item[:100]}...")
            
            if length > 10:
                print(f"  ... 还有 {length - 10} 个任务在队列中")
    
    # 3. 查看任务结果（Hash 类型）
    print("\n📊 任务结果（最近的结果）:")
    print("-" * 80)
    
    result_keys = [key for key in all_keys if 'celery-task-meta' in key]
    if result_keys:
        print(f"  找到 {len(result_keys)} 个任务结果")
        print("  显示最近 5 个:")
        print()
        
        for key in sorted(result_keys, reverse=True)[:5]:
            result_data = r.get(key)
            if result_data:
                try:
                    result = json.loads(result_data)
                    task_id = key.replace('celery-task-meta-', '')
                    status = result.get('status', 'unknown')
                    result_value = result.get('result', 'N/A')
                    
                    print(f"  ID: {task_id[:32]}...")
                    print(f"  状态: {status}")
                    if status == 'SUCCESS':
                        print(f"  结果: {str(result_value)[:100]}")
                    elif status == 'FAILURE':
                        error = result.get('traceback', 'N/A')
                        print(f"  错误: {str(error)[:100]}")
                    print()
                except json.JSONDecodeError:
                    print(f"  {key}: {result_data[:100]}...")
    else:
        print("  未找到任务结果")
    
    # 4. 统计信息
    print("\n📈 统计信息:")
    print("-" * 80)
    info = r.info('stats')
    print(f"  总键数: {len(all_keys)}")
    print(f"  Celery 相关键: {len(celery_keys)}")
    print(f"  队列数: {sum(1 for q in queue_names if r.llen(q) > 0)}")
    print(f"  任务结果数: {len(result_keys)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='查看 Redis 队列内容')
    parser.add_argument('--host', default='localhost', help='Redis 主机地址')
    parser.add_argument('--port', type=int, default=6379, help='Redis 端口')
    parser.add_argument('--db', type=int, default=0, help='Redis 数据库编号')
    parser.add_argument('--password', default=None, help='Redis 密码')
    
    args = parser.parse_args()
    
    view_redis_queues(
        host=args.host,
        port=args.port,
        db=args.db,
        password=args.password
    )


if __name__ == '__main__':
    main()

