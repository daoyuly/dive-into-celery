#!/usr/bin/env python3
"""
查看 Redis 队列内容

演示如何在 Redis 中查看 basic 队列的内容
"""

import sys
from pathlib import Path
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import redis
except ImportError:
    print("❌ 请先安装 redis: pip install redis")
    sys.exit(1)

from celery_app import app


def view_basic_queue():
    """查看 basic 队列内容"""
    print("=" * 80)
    print("查看 Redis basic 队列")
    print("=" * 80)
    
    # 获取 Redis 配置
    broker_url = app.conf.broker_url
    print(f"\nRedis 连接: {broker_url}")
    
    # 解析 Redis URL
    # 格式: redis://[:password@]host[:port][/database]
    if broker_url.startswith('redis://'):
        url_parts = broker_url.replace('redis://', '').split('/')
        if '@' in url_parts[0]:
            # 有密码
            auth, host_port = url_parts[0].split('@')
            password = auth.split(':')[1] if ':' in auth else auth
        else:
            password = None
            host_port = url_parts[0]
        
        host, port = host_port.split(':') if ':' in host_port else (host_port, '6379')
        db = int(url_parts[1]) if len(url_parts) > 1 else 0
    else:
        host = 'localhost'
        port = 6379
        db = 0
        password = None
    
    print(f"  主机: {host}")
    print(f"  端口: {port}")
    print(f"  数据库: {db}")
    print(f"  密码: {'***' if password else '(无)'}")
    
    # 连接 Redis
    try:
        if password:
            r = redis.Redis(host=host, port=int(port), db=db, password=password, decode_responses=True)
        else:
            r = redis.Redis(host=host, port=int(port), db=db, decode_responses=True)
        
        # 测试连接
        r.ping()
        print("\n✅ Redis 连接成功\n")
    except Exception as e:
        print(f"\n❌ Redis 连接失败: {e}")
        return
    
    # 查看 basic 队列
    queue_name = 'basic'
    print(f"📦 队列: {queue_name}")
    print("-" * 80)
    
    # 1. 查看队列长度
    length = r.llen(queue_name)
    print(f"队列长度: {length} 个任务")
    
    if length == 0:
        print("\n队列为空，没有待执行的任务")
        return
    
    # 2. 查看队列中的任务（不删除）
    print(f"\n队列内容（前 10 个任务，不删除）:")
    print("-" * 80)
    
    items = r.lrange(queue_name, 0, 9)  # 获取前10个，不删除
    
    for i, item in enumerate(items, 1):
        print(f"\n[{i}] 任务消息:")
        try:
            # 尝试解析 JSON
            task_data = json.loads(item)
            
            print(f"   任务ID: {task_data.get('id', 'N/A')}")
            print(f"   任务名称: {task_data.get('task', 'N/A')}")
            
            args = task_data.get('args', [])
            kwargs = task_data.get('kwargs', {})
            print(f"   参数: args={args}, kwargs={kwargs}")
            
            retries = task_data.get('retries', 0)
            print(f"   重试次数: {retries}")
            
            eta = task_data.get('eta')
            if eta:
                print(f"   执行时间: {eta}")
            
            expires = task_data.get('expires')
            if expires:
                print(f"   过期时间: {expires}")
            
            # 显示完整消息（可选）
            print(f"   完整消息: {item[:200]}...")
            
        except json.JSONDecodeError:
            print(f"   ⚠️  无法解析 JSON: {item[:100]}...")
    
    if length > 10:
        print(f"\n... 还有 {length - 10} 个任务在队列中")
    
    # 3. 查看队列统计
    print("\n" + "=" * 80)
    print("队列统计")
    print("=" * 80)
    print(f"总任务数: {length}")
    print(f"已显示: {min(10, length)}")
    print(f"剩余: {max(0, length - 10)}")


def view_all_celery_queues():
    """查看所有 Celery 相关的队列"""
    print("\n" + "=" * 80)
    print("查看所有 Celery 队列")
    print("=" * 80)
    
    # 获取 Redis 配置
    broker_url = app.conf.broker_url
    
    # 解析 Redis URL（简化版）
    if '@' in broker_url:
        password = broker_url.split('@')[0].split(':')[-1]
        host_port = broker_url.split('@')[1].split('/')[0]
    else:
        password = None
        host_port = broker_url.replace('redis://', '').split('/')[0]
    
    host, port = host_port.split(':') if ':' in host_port else (host_port, '6379')
    db = int(broker_url.split('/')[-1]) if '/' in broker_url else 0
    
    # 连接 Redis
    try:
        if password:
            r = redis.Redis(host=host, port=int(port), db=db, password=password, decode_responses=True)
        else:
            r = redis.Redis(host=host, port=int(port), db=db, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return
    
    # 获取所有队列名称
    queue_names = ['celery', 'basic', 'advanced', 'realworld']
    
    print("\n队列统计:")
    print("-" * 80)
    for queue_name in queue_names:
        length = r.llen(queue_name)
        status = "🟢" if length > 0 else "⚪"
        print(f"  {status} {queue_name:15s}: {length:4d} 个任务")


def view_redis_cli_commands():
    """显示 Redis CLI 命令"""
    print("\n" + "=" * 80)
    print("使用 Redis CLI 查看队列")
    print("=" * 80)
    
    print("\n1. 连接 Redis")
    print("-" * 80)
    print("   redis-cli")
    print("   # 或指定主机和端口")
    print("   redis-cli -h localhost -p 6379")
    
    print("\n2. 查看队列长度")
    print("-" * 80)
    print("   LLEN basic")
    print("   # 返回队列中的任务数量")
    
    print("\n3. 查看队列内容（不删除）")
    print("-" * 80)
    print("   # 查看前 10 个任务")
    print("   LRANGE basic 0 9")
    print("   # 查看所有任务")
    print("   LRANGE basic 0 -1")
    
    print("\n4. 查看并删除任务（消费任务）")
    print("-" * 80)
    print("   # 阻塞等待并获取任务（Worker 使用的方式）")
    print("   BRPOP basic 0")
    print("   # 非阻塞获取任务")
    print("   RPOP basic")
    
    print("\n5. 查看所有键")
    print("-" * 80)
    print("   KEYS *")
    print("   # 查看 Celery 相关的键")
    print("   KEYS celery*")
    
    print("\n6. 查看任务结果")
    print("-" * 80)
    print("   # 查看任务结果（需要任务ID）")
    print("   GET celery-task-meta-{task_id}")
    
    print("\n7. 清空队列（谨慎使用）")
    print("-" * 80)
    print("   # 删除队列中的所有任务")
    print("   DEL basic")
    print("   # 或使用")
    print("   LTRIM basic 1 0")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Redis 队列查看工具")
    print("=" * 80)
    
    try:
        view_basic_queue()
        view_all_celery_queues()
        view_redis_cli_commands()
        
        print("\n" + "=" * 80)
        print("✅ 查看完成！")
        print("=" * 80)
        print("\n💡 提示:")
        print("  - 使用 Redis CLI 可以更灵活地查看队列")
        print("  - LRANGE 不会删除任务，BRPOP 会删除任务")
        print("  - 使用 python3 redis_queue_viewer.py 可以查看所有队列")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

