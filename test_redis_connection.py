#!/usr/bin/env python3
"""
测试 Redis 连接脚本

用于验证 Docker Redis 连接是否正常
"""

import redis
import os
import sys

def test_redis_connection():
    """测试 Redis 连接"""
    # 从环境变量读取配置，与 celery_app.py 保持一致
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    print("=" * 50)
    print("测试 Redis 连接")
    print("=" * 50)
    print(f"Host: {REDIS_HOST}")
    print(f"Port: {REDIS_PORT}")
    print(f"DB: {REDIS_DB}")
    print(f"Password: {'***' if REDIS_PASSWORD else '(无)'}")
    print("-" * 50)
    
    try:
        # 创建 Redis 连接
        if REDIS_PASSWORD:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
        else:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
        
        # 测试连接
        result = r.ping()
        if result:
            print("✅ Redis 连接成功！")
            
            # 获取 Redis 信息
            info = r.info()
            print(f"\nRedis 版本: {info.get('redis_version', 'N/A')}")
            print(f"运行模式: {info.get('redis_mode', 'N/A')}")
            print(f"已用内存: {info.get('used_memory_human', 'N/A')}")
            
            # 测试写入和读取
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            if value == 'test_value':
                print("✅ 读写测试成功！")
                r.delete('test_key')
            
            return True
        else:
            print("❌ Redis 连接失败")
            return False
            
    except redis.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        print("\n💡 提示:")
        print("1. 确保 Redis 正在运行")
        print("2. 检查端口是否正确")
        print("3. 如果使用 Docker，确保端口已映射")
        return False
    except redis.AuthenticationError as e:
        print(f"❌ 认证错误: {e}")
        print("\n💡 提示: 检查 Redis 密码是否正确")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False


def test_celery_connection():
    """测试 Celery 连接"""
    print("\n" + "=" * 50)
    print("测试 Celery 连接")
    print("=" * 50)
    
    try:
        from celery_app import app
        
        # 检查连接
        inspect = app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            print("✅ 检测到活跃的 Celery Workers:")
            for worker, tasks in active_workers.items():
                print(f"  - {worker}: {len(tasks)} 个任务")
        else:
            print("⚠️  未检测到活跃的 Workers")
            print("💡 提示: 请先启动 Celery Worker:")
            print("   celery -A celery_app worker --loglevel=info")
        
        return True
    except Exception as e:
        print(f"❌ Celery 连接错误: {e}")
        return False


if __name__ == '__main__':
    print("\n🔍 开始测试 Redis 连接...\n")
    
    redis_ok = test_redis_connection()
    celery_ok = test_celery_connection()
    
    print("\n" + "=" * 50)
    if redis_ok:
        print("✅ Redis 连接正常")
    else:
        print("❌ Redis 连接失败")
        sys.exit(1)
    
    if celery_ok:
        print("✅ Celery 配置正常")
    else:
        print("⚠️  Celery Worker 未运行（这是正常的，如果还没启动）")
    
    print("=" * 50)

