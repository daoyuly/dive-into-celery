"""
Eventlet 使用演示

演示如何使用 Eventlet 池启动 Celery Worker
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demonstrate_installation():
    """演示安装"""
    print("=" * 80)
    print("Eventlet 安装")
    print("=" * 80)
    
    print("\n1. 安装 Eventlet")
    print("-" * 80)
    print("""
  # 使用 pip
  pip install eventlet
  
  # 使用 uv
  uv pip install eventlet
  
  # 指定版本
  pip install eventlet==0.33.3
    """)
    
    print("\n2. 验证安装")
    print("-" * 80)
    print("""
  python3 -c "import eventlet; print(eventlet.__version__)"
  # 应该输出版本号，如: 0.33.3
    """)
    
    # 尝试导入
    try:
        import eventlet
        print(f"\n✅ Eventlet 已安装，版本: {eventlet.__version__}")
    except ImportError:
        print("\n❌ Eventlet 未安装，请运行: pip install eventlet")


def demonstrate_basic_usage():
    """演示基本使用"""
    print("\n" + "=" * 80)
    print("基本使用")
    print("=" * 80)
    
    print("\n1. 启动 Worker（基本命令）")
    print("-" * 80)
    print("""
  celery -A celery_app worker \\
      --pool=eventlet \\
      --concurrency=50 \\
      --loglevel=info
    """)
    
    print("\n2. 完整启动命令")
    print("-" * 80)
    print("""
  celery -A celery_app worker \\
      --pool=eventlet \\
      --concurrency=50 \\
      --loglevel=info \\
      --hostname=worker@%h \\
      --queues=basic,advanced,realworld \\
      --max-tasks-per-child=1000
    """)
    
    print("\n3. 参数说明")
    print("-" * 80)
    print("""
  --pool=eventlet        # 使用 Eventlet 池（必需）
  --concurrency=50       # 并发数（协程数），可以设置很高
  --loglevel=info        # 日志级别
  --hostname=worker@%h   # Worker 名称
  --queues=basic         # 监听的队列
  --max-tasks-per-child  # 每个协程执行的最大任务数
    """)


def demonstrate_configuration():
    """演示配置"""
    print("\n" + "=" * 80)
    print("配置方式")
    print("=" * 80)
    
    print("\n方式 1: 启动参数（推荐）")
    print("-" * 80)
    print("""
  celery -A celery_app worker --pool=eventlet --concurrency=50
    """)
    
    print("\n方式 2: 配置文件")
    print("-" * 80)
    print("""
  # celery_app.py
  app.conf.update(
      worker_pool='eventlet',
      worker_concurrency=50,
  )
    """)
    
    print("\n方式 3: 环境变量")
    print("-" * 80)
    print("""
  export CELERY_WORKER_POOL=eventlet
  export CELERY_WORKER_CONCURRENCY=50
  celery -A celery_app worker
    """)


def demonstrate_concurrency_settings():
    """演示并发数设置"""
    print("\n" + "=" * 80)
    print("并发数设置")
    print("=" * 80)
    
    print("\n1. I/O 密集型任务")
    print("-" * 80)
    print("""
  # 网络请求、数据库查询、文件操作
  --concurrency=100  # 可以设置很高
    """)
    
    print("\n2. 混合任务")
    print("-" * 80)
    print("""
  # 既有 I/O 又有计算
  --concurrency=50   # 中等并发
    """)
    
    print("\n3. CPU 密集型任务")
    print("-" * 80)
    print("""
  # 不推荐使用 eventlet，应该用 prefork
  --pool=prefork --concurrency=4
    """)
    
    print("\n4. 并发数建议")
    print("-" * 80)
    print("""
  开发环境: 10-20
  生产环境: 50-200
  高负载场景: 200-1000
    """)


def demonstrate_verification():
    """演示验证方法"""
    print("\n" + "=" * 80)
    print("验证 Eventlet 是否工作")
    print("=" * 80)
    
    print("\n方法 1: 查看启动日志")
    print("-" * 80)
    print("""
  celery -A celery_app worker --pool=eventlet --concurrency=50
  
  应该看到:
  [INFO/MainProcess] Connected to redis://localhost:6379/0
  [INFO/MainProcess] celery@hostname ready.
  
  不应该看到:
  [INFO/ForkPoolWorker-1] ...  # 这是 prefork 的日志
    """)
    
    print("\n方法 2: 使用 Python 检查")
    print("-" * 80)
    print("""
  from celery_app import app
  
  inspect = app.control.inspect()
  stats = inspect.stats()
  
  for worker, worker_stats in stats.items():
      pool = worker_stats.get('pool', {})
      print(f"{worker}: {pool}")
      # 应该显示: {'implementation': 'eventlet'}
    """)
    
    print("\n方法 3: 测试高并发")
    print("-" * 80)
    print("""
  from tasks.basic_tasks import add
  from celery import group
  
  # 提交 100 个任务
  job = group(add.s(i, i) for i in range(100))
  result = job.apply_async()
  
  # Eventlet 池可以快速处理
  print(result.get(timeout=10))
    """)


def demonstrate_comparison():
    """演示对比"""
    print("\n" + "=" * 80)
    print("Eventlet vs Prefork")
    print("=" * 80)
    
    print("\n对比表:")
    print("-" * 80)
    print("""
  | 特性 | Eventlet | Prefork |
  |------|----------|---------|
  | 类型 | 协程 | 多进程 |
  | 并发数 | 50-1000+ | CPU 核心数 |
  | 内存占用 | 低 | 高 |
  | CPU 密集型 | ❌ 差 | ✅ 最佳 |
  | I/O 密集型 | ✅ 最佳 | ⚠️ 一般 |
  | 多进程问题 | ✅ 无 | ❌ 有 |
    """)
    
    print("\n选择建议:")
    print("-" * 80)
    print("""
  - I/O 密集型任务 → Eventlet
  - CPU 密集型任务 → Prefork
  - 需要避免多进程问题 → Eventlet
  - 需要高并发 → Eventlet
    """)


def demonstrate_best_practices():
    """演示最佳实践"""
    print("\n" + "=" * 80)
    print("最佳实践")
    print("=" * 80)
    
    print("\n1. 开发环境")
    print("-" * 80)
    print("""
  celery -A celery_app worker \\
      --pool=eventlet \\
      --concurrency=10 \\
      --loglevel=debug
    """)
    
    print("\n2. 生产环境")
    print("-" * 80)
    print("""
  celery -A celery_app worker \\
      --pool=eventlet \\
      --concurrency=100 \\
      --loglevel=info \\
      --max-tasks-per-child=1000
    """)
    
    print("\n3. 高负载场景")
    print("-" * 80)
    print("""
  celery -A celery_app worker \\
      --pool=eventlet \\
      --concurrency=500 \\
      --loglevel=warning
    """)


def demonstrate_actual_command():
    """演示实际命令"""
    print("\n" + "=" * 80)
    print("实际使用命令")
    print("=" * 80)
    
    print("\n针对你的场景（ushow_nlp）:")
    print("-" * 80)
    print("""
  # 1. 安装 Eventlet
  pip install eventlet
  
  # 2. 启动 Worker（推荐配置）
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=eventlet \\
      --concurrency=100 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp \\
      --max-tasks-per-child=1000
  
  # 3. 验证是否工作
  # 查看日志，应该看到 eventlet 相关的信息
  # 不应该看到 ForkPoolWorker 的日志
    """)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Eventlet 使用指南")
    print("=" * 80)
    
    try:
        demonstrate_installation()
        demonstrate_basic_usage()
        demonstrate_configuration()
        demonstrate_concurrency_settings()
        demonstrate_verification()
        demonstrate_comparison()
        demonstrate_best_practices()
        demonstrate_actual_command()
        
        print("\n" + "=" * 80)
        print("✅ 演示完成！")
        print("=" * 80)
        print("\n💡 快速开始:")
        print("  1. pip install eventlet")
        print("  2. celery -A celery_app worker --pool=eventlet --concurrency=50")
        print("  3. 详细说明请查看: EVENTLET_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

