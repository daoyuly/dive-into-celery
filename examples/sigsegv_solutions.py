"""
SIGSEGV 错误解决方案演示

演示如何解决 Celery Worker 的 SIGSEGV 错误
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demonstrate_sigsegv_analysis():
    """演示 SIGSEGV 错误分析"""
    print("=" * 80)
    print("SIGSEGV 错误分析")
    print("=" * 80)
    
    print("\n错误信息:")
    print("-" * 80)
    print("""
  Process 'ForkPoolWorker-1' pid:31 exited with 'signal 11 (SIGSEGV)'
  WorkerLostError: Worker exited prematurely: signal 11 (SIGSEGV)
  ChordError: Dependency raised WorkerLostError
    """)
    
    print("\n错误类型:")
    print("-" * 80)
    print("""
  SIGSEGV (Signal 11): 段错误
  - 程序访问了不应该访问的内存地址
  - 导致进程立即终止
  - 通常由多进程问题引起
    """)


def demonstrate_solutions():
    """演示解决方案"""
    print("\n" + "=" * 80)
    print("解决方案（按优先级）")
    print("=" * 80)
    
    print("\n方案 1: 使用 Eventlet 池（最推荐）")
    print("-" * 80)
    print("""
  # 安装 eventlet
  pip install eventlet
  
  # 启动 Worker
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=eventlet \\
      --concurrency=50 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp \\
      --max-tasks-per-child=1000
  
  优点:
    ✅ 避免多进程问题（SIGSEGV 的主要原因）
    ✅ 性能好，可以高并发
    ✅ 适合大多数任务类型
  
  缺点:
    ❌ 不适合 CPU 密集型任务
    ❌ 需要安装 eventlet
    """)
    
    print("\n方案 2: 使用 Solo 池（快速验证）")
    print("-" * 80)
    print("""
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=solo \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp
  
  优点:
    ✅ 单线程，避免多进程问题
    ✅ 易于调试
    ✅ 可以快速验证问题
  
  缺点:
    ❌ 性能极差，无法并发
    ❌ 仅适合调试
    """)
    
    print("\n方案 3: 优化 Prefork 配置")
    print("-" * 80)
    print("""
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=prefork \\
      --concurrency=2 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp \\
      --max-tasks-per-child=50 \\
      --time-limit=300 \\
      --soft-time-limit=240
  
  改进点:
    ✅ 降低并发数（减少进程数）
    ✅ 更频繁重启进程（防止内存问题）
    ✅ 添加超时限制
    """)


def demonstrate_code_fixes():
    """演示代码修复"""
    print("\n" + "=" * 80)
    print("任务代码修复建议")
    print("=" * 80)
    
    print("\n1. 避免全局变量")
    print("-" * 80)
    print("""
  # ❌ 不好的做法
  global_var = []
  
  @app.task
  def my_task():
      global global_var
      global_var.append(...)  # 多进程下可能有问题
  
  # ✅ 好的做法
  @app.task
  def my_task():
      local_var = []  # 使用局部变量
      local_var.append(...)
      return local_var
    """)
    
    print("\n2. 正确管理资源")
    print("-" * 80)
    print("""
  # ✅ 好的做法
  @app.task
  def my_task():
      resource = acquire_resource()
      try:
          result = process(resource)
          return result
      finally:
          release_resource(resource)  # 确保释放
    """)
    
    print("\n3. 处理 C 扩展库")
    print("-" * 80)
    print("""
  # ✅ 在任务内部导入和初始化
  @app.task
  def my_task():
      import numpy as np
      np.random.seed()  # 重置随机种子
      # 任务逻辑
    """)


def demonstrate_diagnosis_steps():
    """演示诊断步骤"""
    print("\n" + "=" * 80)
    print("诊断步骤")
    print("=" * 80)
    
    print("\n步骤 1: 确认问题范围")
    print("-" * 80)
    print("""
  # 使用 solo 池测试
  celery -A ushow_nlp worker --pool=solo --queues=ai.ushow_nlp
  
  - 如果 solo 池正常 → 多进程问题
  - 如果 solo 池也崩溃 → 任务代码问题
    """)
    
    print("\n步骤 2: 检查任务代码")
    print("-" * 80)
    print("""
  检查任务中是否使用了:
  1. C 扩展库（NumPy, Pandas, OpenCV 等）
  2. 全局变量
  3. 共享资源
  4. 多线程/多进程混用
    """)
    
    print("\n步骤 3: 检查依赖库")
    print("-" * 80)
    print("""
  # 检查库版本
  pip list | grep -E "numpy|pandas|opencv"
  
  # 更新可能有问题的库
  pip install --upgrade numpy pandas
    """)
    
    print("\n步骤 4: 添加详细日志")
    print("-" * 80)
    print("""
  # 使用 debug 日志级别
  celery -A ushow_nlp worker \\
      --loglevel=debug \\
      --pool=prefork \\
      --concurrency=1 \\
      --queues=ai.ushow_nlp
    """)


def demonstrate_recommended_config():
    """演示推荐配置"""
    print("\n" + "=" * 80)
    print("推荐配置（生产环境）")
    print("=" * 80)
    
    print("\nI/O 密集型任务（推荐）")
    print("-" * 80)
    print("""
  pip install eventlet
  
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=eventlet \\
      --concurrency=50 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp \\
      --max-tasks-per-child=1000
    """)
    
    print("\nCPU 密集型任务（如果必须使用 prefork）")
    print("-" * 80)
    print("""
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=prefork \\
      --concurrency=2 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp \\
      --max-tasks-per-child=50 \\
      --time-limit=300 \\
      --soft-time-limit=240
    """)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("SIGSEGV 错误解决方案")
    print("=" * 80)
    
    try:
        demonstrate_sigsegv_analysis()
        demonstrate_solutions()
        demonstrate_code_fixes()
        demonstrate_diagnosis_steps()
        demonstrate_recommended_config()
        
        print("\n" + "=" * 80)
        print("✅ 解决方案演示完成！")
        print("=" * 80)
        print("\n💡 关键建议:")
        print("  1. 最推荐: 使用 eventlet 池避免多进程问题")
        print("  2. 快速验证: 使用 solo 池确认问题")
        print("  3. 检查代码: 避免全局变量和 C 扩展库问题")
        print("  4. 详细说明请查看: SIGSEGV_TROUBLESHOOTING.md")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

