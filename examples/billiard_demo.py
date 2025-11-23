"""
Billiard 多进程管理演示

这个脚本演示了 Billiard（Celery 使用的多进程管理工具）的使用
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import time


def demonstrate_billiard_import():
    """演示 Billiard 的导入"""
    print("=" * 70)
    print("演示1: Billiard 导入和基本信息")
    print("=" * 70)
    
    try:
        import billiard
        
        print("\n✓ Billiard 已安装")
        print(f"  版本: {billiard.__version__}")
        print(f"  路径: {billiard.__file__}")
        
        # 对比 multiprocessing
        import multiprocessing
        print(f"\n对比 Multiprocessing:")
        print(f"  Multiprocessing 版本: {multiprocessing.__version__}")
        print(f"  Multiprocessing 路径: {multiprocessing.__file__}")
        
        print("\n说明:")
        print("  - Billiard 是 multiprocessing 的 fork")
        print("  - 专门为 Celery 优化")
        print("  - API 与 multiprocessing 基本相同")
        
    except ImportError:
        print("\n✗ Billiard 未安装")
        print("  安装命令: pip install billiard")
        print("  或: pip install celery  # Celery 会自动安装 billiard")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_process_pool():
    """演示进程池的使用"""
    print("=" * 70)
    print("演示2: Billiard 进程池")
    print("=" * 70)
    
    try:
        from billiard import Pool
        
        def worker_task(x):
            """Worker 任务函数"""
            pid = os.getpid()
            print(f"  进程 {pid}: 处理任务 {x}")
            time.sleep(0.5)  # 模拟处理时间
            return x * 2
        
        print("\n创建进程池（4 个进程）:")
        with Pool(processes=4) as pool:
            print("  进程池已创建")
            
            # 提交任务
            print("\n提交 8 个任务:")
            results = []
            for i in range(8):
                result = pool.apply_async(worker_task, (i,))
                results.append(result)
                print(f"  任务 {i} 已提交")
            
            # 获取结果
            print("\n等待所有任务完成...")
            final_results = [r.get() for r in results]
            
            print(f"\n所有任务完成:")
            for i, result in enumerate(final_results):
                print(f"  任务 {i} 结果: {result}")
        
        print("\n进程池已关闭")
        
    except ImportError:
        print("\n✗ Billiard 未安装，跳过演示")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_process_creation():
    """演示进程创建"""
    print("=" * 70)
    print("演示3: 进程创建和 PID")
    print("=" * 70)
    
    try:
        from billiard import Process
        
        def child_process(name):
            """子进程函数"""
            pid = os.getpid()
            ppid = os.getppid()
            print(f"  子进程 {name}:")
            print(f"    PID: {pid}")
            print(f"    PPID (父进程): {ppid}")
            time.sleep(1)
            return f"进程 {name} 完成"
        
        print("\n主进程信息:")
        print(f"  PID: {os.getpid()}")
        print(f"  PPID: {os.getppid()}")
        
        print("\n创建 3 个子进程:")
        processes = []
        for i in range(3):
            p = Process(target=child_process, args=(f"Worker-{i+1}",))
            processes.append(p)
            p.start()
            print(f"  子进程 {i+1} 已启动 (PID: {p.pid})")
        
        print("\n等待所有子进程完成...")
        for p in processes:
            p.join()
            print(f"  子进程 {p.pid} 已完成")
        
    except ImportError:
        print("\n✗ Billiard 未安装，跳过演示")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_process_communication():
    """演示进程间通信"""
    print("=" * 70)
    print("演示4: 进程间通信（Queue）")
    print("=" * 70)
    
    try:
        from billiard import Process, Queue
        
        def producer(queue, items):
            """生产者进程"""
            pid = os.getpid()
            print(f"  生产者进程 {pid}: 开始生产")
            for item in items:
                queue.put(item)
                print(f"    生产: {item}")
                time.sleep(0.2)
            queue.put(None)  # 结束信号
            print(f"  生产者进程 {pid}: 完成")
        
        def consumer(queue, name):
            """消费者进程"""
            pid = os.getpid()
            print(f"  消费者进程 {name} ({pid}): 开始消费")
            while True:
                item = queue.get()
                if item is None:
                    break
                print(f"    消费: {item}")
                time.sleep(0.3)
            print(f"  消费者进程 {name} ({pid}): 完成")
        
        # 创建队列
        queue = Queue()
        
        # 创建进程
        producer_p = Process(target=producer, args=(queue, [1, 2, 3, 4, 5]))
        consumer_p = Process(target=consumer, args=(queue, "Consumer-1"))
        
        print("\n启动生产者和消费者:")
        producer_p.start()
        consumer_p.start()
        
        print("\n等待进程完成...")
        producer_p.join()
        consumer_p.join()
        
        print("\n所有进程完成")
        
    except ImportError:
        print("\n✗ Billiard 未安装，跳过演示")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_celery_usage():
    """演示 Celery 如何使用 Billiard"""
    print("=" * 70)
    print("演示5: Celery 如何使用 Billiard")
    print("=" * 70)
    
    print("\nCelery 内部使用 Billiard 的方式:")
    print("""
  1. 创建进程池:
     from billiard import Pool
     pool = Pool(processes=4)
  
  2. 子进程初始化:
     def worker_init():
         # 重新连接 Redis/RabbitMQ
         # 加载任务代码
         pass
     
     pool = Pool(processes=4, initializer=worker_init)
  
  3. 执行任务:
     result = pool.apply_async(execute_task, (task,))
  
  4. 关闭进程池:
     pool.close()
     pool.join()
    """)
    
    print("\n实际使用:")
    print("  当你运行: celery -A celery_app worker --concurrency=4")
    print("  Celery 内部会:")
    print("    1. 创建 Billiard Pool（4 个进程）")
    print("    2. 每个子进程进入工作循环")
    print("    3. 从消息队列获取任务")
    print("    4. 执行任务并返回结果")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_process_monitoring():
    """演示进程监控"""
    print("=" * 70)
    print("演示6: 进程监控")
    print("=" * 70)
    
    try:
        import psutil
        from billiard import Process
        
        def monitored_task(name, duration):
            """被监控的任务"""
            pid = os.getpid()
            print(f"  任务 {name} (PID: {pid}): 开始执行")
            
            # 模拟 CPU 密集型任务
            start = time.time()
            result = 0
            while time.time() - start < duration:
                result += 1
            
            print(f"  任务 {name} (PID: {pid}): 完成，结果: {result}")
            return result
        
        print("\n创建并监控进程:")
        processes = []
        for i in range(2):
            p = Process(target=monitored_task, args=(f"Task-{i+1}", 2))
            processes.append(p)
            p.start()
        
        # 监控进程
        print("\n监控进程状态:")
        for p in processes:
            try:
                proc = psutil.Process(p.pid)
                print(f"  进程 {p.pid}:")
                print(f"    状态: {proc.status()}")
                print(f"    CPU: {proc.cpu_percent():.1f}%")
                print(f"    内存: {proc.memory_info().rss / 1024 / 1024:.2f} MB")
            except Exception as e:
                print(f"  进程 {p.pid}: 无法监控 ({e})")
        
        # 等待完成
        for p in processes:
            p.join()
        
        print("\n所有进程完成")
        
    except ImportError:
        print("\n⚠️  psutil 未安装，跳过监控演示")
        print("  安装命令: pip install psutil")
    
    print("\n" + "-" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Billiard 多进程管理演示")
    print("=" * 70 + "\n")
    
    # 运行演示
    demonstrate_billiard_import()
    
    input("按 Enter 键继续进程池演示...")
    demonstrate_process_pool()
    
    input("按 Enter 键继续进程创建演示...")
    demonstrate_process_creation()
    
    input("按 Enter 键继续进程通信演示...")
    demonstrate_process_communication()
    
    input("按 Enter 键继续 Celery 使用演示...")
    demonstrate_celery_usage()
    
    input("按 Enter 键继续进程监控演示...")
    demonstrate_process_monitoring()
    
    print("\n" + "=" * 70)
    print("所有演示完成！")
    print("=" * 70 + "\n")
    print("详细分析请参考: doc/CELERY_PROCESS_MANAGEMENT.md")

