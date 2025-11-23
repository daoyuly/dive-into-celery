"""
Kombu 使用演示

这个脚本演示了 Kombu 的核心功能，包括：
1. Connection 管理
2. Producer 发送消息
3. Consumer 接收消息
4. 队列管理
5. 序列化机制
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kombu import Connection, Producer, Consumer, Queue, Exchange
from kombu.serialization import registry
import json
import time


def demonstrate_connection():
    """演示 Connection 的使用"""
    print("=" * 70)
    print("演示1: Connection 管理")
    print("=" * 70)
    
    # 创建连接
    conn = Connection('redis://localhost:6379/0')
    
    print("\n连接信息:")
    print(f"  Hostname: {conn.hostname}")
    print(f"  Transport: {conn.transport_cls}")
    
    # 使用上下文管理器
    print("\n使用上下文管理器（自动管理连接）:")
    with Connection('redis://localhost:6379/0') as conn:
        print("  连接已建立")
        # 连接在使用后自动关闭
    
    print("  连接已关闭")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_producer():
    """演示 Producer 的使用"""
    print("=" * 70)
    print("演示2: Producer 发送消息")
    print("=" * 70)
    
    # 创建连接和队列
    conn = Connection('redis://localhost:6379/0')
    queue = Queue('kombu_demo_queue')
    
    print("\n发送消息到队列 'kombu_demo_queue':")
    
    with conn.Producer() as producer:
        # 发送简单消息
        message1 = {'type': 'greeting', 'content': 'Hello, Kombu!'}
        producer.publish(
            message1,
            queue=queue,
            serializer='json'
        )
        print(f"  ✓ 消息1已发送: {message1}")
        
        # 发送复杂消息
        message2 = {
            'type': 'data',
            'items': [1, 2, 3, 4, 5],
            'metadata': {'timestamp': time.time()}
        }
        producer.publish(
            message2,
            queue=queue,
            serializer='json'
        )
        print(f"  ✓ 消息2已发送: {message2}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_consumer():
    """演示 Consumer 的使用"""
    print("=" * 70)
    print("演示3: Consumer 接收消息")
    print("=" * 70)
    
    # 创建连接和队列
    conn = Connection('redis://localhost:6379/0')
    queue = Queue('kombu_demo_queue')
    
    # 定义消息处理函数
    received_messages = []
    
    def process_message(body, message):
        """处理消息的回调函数"""
        print(f"\n收到消息:")
        print(f"  内容: {body}")
        print(f"  消息ID: {message.delivery_info.get('delivery_tag', 'N/A')}")
        
        received_messages.append(body)
        
        # 确认消息
        message.ack()
        print("  消息已确认")
    
    print("\n等待接收消息（最多等待 5 秒）...")
    
    try:
        with conn.Consumer(queue, callbacks=[process_message]) as consumer:
            # 开始消费
            consumer.consume()
            
            # 等待消息（最多 5 秒）
            conn.drain_events(timeout=5)
            
            print(f"\n总共收到 {len(received_messages)} 条消息")
    except Exception as e:
        print(f"\n接收消息时出错: {e}")
        print("提示: 请确保 Redis 正在运行，并且队列中有消息")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_queue_operations():
    """演示队列操作"""
    print("=" * 70)
    print("演示4: 队列操作")
    print("=" * 70)
    
    conn = Connection('redis://localhost:6379/0')
    queue = Queue('kombu_demo_queue2')
    
    print("\n队列信息:")
    print(f"  队列名称: {queue.name}")
    print(f"  交换机: {queue.exchange}")
    print(f"  路由键: {queue.routing_key}")
    
    # 声明队列
    print("\n声明队列:")
    with conn.channel() as channel:
        queue.declare(channel=channel)
        print("  ✓ 队列已声明")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_serialization():
    """演示序列化机制"""
    print("=" * 70)
    print("演示5: 序列化机制")
    print("=" * 70)
    
    # 获取 JSON 序列化器
    json_serializer = registry.get('json')
    
    # 测试数据
    data = {
        'name': 'Kombu Demo',
        'numbers': [1, 2, 3, 4, 5],
        'nested': {
            'key1': 'value1',
            'key2': 'value2'
        }
    }
    
    print("\n原始数据:")
    print(f"  {data}")
    
    # 序列化
    serialized = json_serializer.dumps(data)
    print(f"\n序列化后 (bytes):")
    print(f"  {serialized}")
    print(f"  长度: {len(serialized)} 字节")
    
    # 反序列化
    deserialized = json_serializer.loads(serialized)
    print(f"\n反序列化后:")
    print(f"  {deserialized}")
    
    # 验证数据一致性
    assert data == deserialized, "序列化/反序列化失败"
    print("\n  ✓ 序列化/反序列化成功，数据一致")
    
    print("\n支持的序列化格式:")
    for name in registry._encoders.keys():
        print(f"  - {name}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_producer_consumer_flow():
    """演示完整的生产者-消费者流程"""
    print("=" * 70)
    print("演示6: 完整的生产者-消费者流程")
    print("=" * 70)
    
    conn = Connection('redis://localhost:6379/0')
    queue = Queue('kombu_demo_flow')
    
    # 生产者：发送消息
    print("\n[生产者] 发送消息...")
    with conn.Producer() as producer:
        for i in range(3):
            message = {
                'id': i + 1,
                'content': f'Message {i + 1}',
                'timestamp': time.time()
            }
            producer.publish(
                message,
                queue=queue,
                serializer='json'
            )
            print(f"  ✓ 消息 {i + 1} 已发送")
    
    # 等待一下，确保消息已到达队列
    time.sleep(0.5)
    
    # 消费者：接收消息
    print("\n[消费者] 接收消息...")
    received_count = 0
    
    def process_message(body, message):
        nonlocal received_count
        received_count += 1
        print(f"  ✓ 收到消息 {body['id']}: {body['content']}")
        message.ack()
    
    try:
        with conn.Consumer(queue, callbacks=[process_message]) as consumer:
            consumer.consume()
            
            # 接收所有消息（最多等待 5 秒）
            start_time = time.time()
            while received_count < 3 and (time.time() - start_time) < 5:
                conn.drain_events(timeout=1)
        
        print(f"\n总共收到 {received_count} 条消息")
    except Exception as e:
        print(f"\n接收消息时出错: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_error_handling():
    """演示错误处理"""
    print("=" * 70)
    print("演示7: 错误处理")
    print("=" * 70)
    
    from kombu.exceptions import OperationalError
    
    # 测试无效连接
    print("\n测试无效连接:")
    try:
        invalid_conn = Connection('redis://invalid_host:6379/0')
        with invalid_conn.Producer() as producer:
            producer.publish({'test': 'data'}, queue=Queue('test'))
    except OperationalError as e:
        print(f"  ✓ 捕获连接错误: {type(e).__name__}")
        print(f"    错误信息: {str(e)[:100]}...")
    
    # 测试消息处理错误
    print("\n测试消息处理错误:")
    conn = Connection('redis://localhost:6379/0')
    queue = Queue('kombu_demo_error')
    
    # 发送一条消息
    with conn.Producer() as producer:
        producer.publish({'test': 'error_handling'}, queue=queue, serializer='json')
    
    def process_with_error(body, message):
        """会抛出异常的处理函数"""
        print(f"  处理消息: {body}")
        raise ValueError("模拟处理错误")
    
    def process_with_error_handling(body, message):
        """带错误处理的处理函数"""
        try:
            print(f"  处理消息: {body}")
            raise ValueError("模拟处理错误")
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            # 拒绝消息（不重新入队）
            message.reject(requeue=False)
    
    print("\n使用错误处理:")
    try:
        with conn.Consumer(queue, callbacks=[process_with_error_handling]) as consumer:
            consumer.consume()
            conn.drain_events(timeout=2)
    except Exception as e:
        print(f"  捕获异常: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_connection_pool():
    """演示连接池的使用"""
    print("=" * 70)
    print("演示8: 连接池管理")
    print("=" * 70)
    
    from kombu import pools
    
    print("\n连接池配置:")
    print(f"  当前连接池限制: {pools.limit}")
    
    # 设置连接池大小
    pools.set_limit(5)
    print(f"  设置连接池限制为: 5")
    
    # 使用连接池
    print("\n使用连接池获取连接:")
    broker_url = 'redis://localhost:6379/0'
    
    # 第一次获取连接
    with pools.connections[broker_url].acquire() as conn1:
        print("  ✓ 获取连接 1")
        producer1 = Producer(conn1)
        producer1.publish({'id': 1}, queue=Queue('pool_test'), serializer='json')
    
    # 第二次获取连接（可能复用连接池中的连接）
    with pools.connections[broker_url].acquire() as conn2:
        print("  ✓ 获取连接 2")
        producer2 = Producer(conn2)
        producer2.publish({'id': 2}, queue=Queue('pool_test'), serializer='json')
    
    print("\n连接已返回到连接池")
    
    print("\n" + "-" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Kombu 使用演示")
    print("=" * 70 + "\n")
    
    print("⚠️  注意: 以下演示需要 Redis 正在运行")
    print("   请确保 Redis 已启动: redis-server\n")
    
    # 运行演示
    demonstrate_connection()
    
    input("按 Enter 键继续 Producer 演示...")
    demonstrate_producer()
    
    input("按 Enter 键继续 Consumer 演示...")
    demonstrate_consumer()
    
    input("按 Enter 键继续队列操作演示...")
    demonstrate_queue_operations()
    
    input("按 Enter 键继续序列化演示...")
    demonstrate_serialization()
    
    input("按 Enter 键继续完整流程演示...")
    demonstrate_producer_consumer_flow()
    
    input("按 Enter 键继续错误处理演示...")
    demonstrate_error_handling()
    
    input("按 Enter 键继续连接池演示...")
    demonstrate_connection_pool()
    
    print("\n" + "=" * 70)
    print("所有演示完成！")
    print("=" * 70 + "\n")
    print("详细分析请参考: doc/KOMBU_DEEP_DIVE.md")

