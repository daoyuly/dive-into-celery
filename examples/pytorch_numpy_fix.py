"""
PyTorch/NumPy 警告修复示例

演示如何修复 "NumPy array is not writeable" 警告
"""

import sys
from pathlib import Path
import numpy as np
import torch

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demonstrate_problem():
    """演示问题"""
    print("=" * 80)
    print("PyTorch/NumPy 警告问题演示")
    print("=" * 80)
    
    print("\n1. 问题代码")
    print("-" * 80)
    print("""
  # ❌ 原始代码（会产生警告）
  model_output = torch.tensor(result.as_numpy(model_config[self.model_name]["return_res"]))
    """)
    
    print("\n2. 警告信息")
    print("-" * 80)
    print("""
  WARNING: The given NumPy array is not writeable, and PyTorch does not support non-writeable tensors.
    """)
    
    print("\n3. 问题原因")
    print("-" * 80)
    print("""
  - NumPy 数组是只读的（not writeable）
  - PyTorch 需要可写的张量
  - 多进程环境下，数组可能来自共享内存，被标记为只读
    """)


def demonstrate_solutions():
    """演示解决方案"""
    print("\n" + "=" * 80)
    print("解决方案")
    print("=" * 80)
    
    print("\n方案 1: 使用 copy()（最简单）")
    print("-" * 80)
    print("""
  # ✅ 修复代码
  numpy_array = result.as_numpy(model_config[self.model_name]["return_res"])
  numpy_array = numpy_array.copy()  # 创建可写副本
  model_output = torch.from_numpy(numpy_array)
    """)
    
    print("\n方案 2: 检查并修复")
    print("-" * 80)
    print("""
  # ✅ 检查并修复
  numpy_array = result.as_numpy(model_config[self.model_name]["return_res"])
  
  if not numpy_array.flags.writeable:
      numpy_array = numpy_array.copy()
  
  model_output = torch.from_numpy(numpy_array)
    """)
    
    print("\n方案 3: 使用工具函数（推荐）")
    print("-" * 80)
    print("""
  def safe_numpy_to_tensor(numpy_array, dtype=None):
      \"\"\"安全地将 NumPy 数组转换为 PyTorch 张量\"\"\"
      if not isinstance(numpy_array, np.ndarray):
          numpy_array = np.array(numpy_array)
      
      if not numpy_array.flags.writeable:
          numpy_array = numpy_array.copy()
      
      if dtype is not None:
          return torch.tensor(numpy_array, dtype=dtype)
      else:
          return torch.from_numpy(numpy_array)
  
  # 使用
  model_output = safe_numpy_to_tensor(
      result.as_numpy(model_config[self.model_name]["return_res"])
  )
    """)


def demonstrate_actual_fix():
    """演示实际修复"""
    print("\n" + "=" * 80)
    print("实际修复演示")
    print("=" * 80)
    
    # 创建一个只读数组（模拟问题场景）
    print("\n1. 创建只读数组（模拟问题）")
    print("-" * 80)
    
    # 创建一个数组
    original_array = np.array([1, 2, 3, 4, 5], dtype=np.float32)
    print(f"   原始数组: {original_array}")
    print(f"   可写: {original_array.flags.writeable}")
    
    # 创建只读视图（模拟多进程环境）
    read_only_array = original_array.view()
    read_only_array.setflags(write=False)
    print(f"\n   只读数组: {read_only_array}")
    print(f"   可写: {read_only_array.flags.writeable}")
    
    print("\n2. 尝试直接转换（会产生警告）")
    print("-" * 80)
    try:
        # 这会触发警告
        tensor = torch.from_numpy(read_only_array)
        print(f"   张量创建成功: {tensor}")
        print(f"   ⚠️  但会产生警告（数组不可写）")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print("\n3. 使用修复方案（无警告）")
    print("-" * 80)
    
    # 修复：复制数组
    writable_array = read_only_array.copy()
    print(f"   复制后数组: {writable_array}")
    print(f"   可写: {writable_array.flags.writeable}")
    
    # 转换为张量
    tensor = torch.from_numpy(writable_array)
    print(f"   张量: {tensor}")
    print(f"   ✅ 无警告，转换成功")


def demonstrate_safe_function():
    """演示安全转换函数"""
    print("\n" + "=" * 80)
    print("安全转换函数")
    print("=" * 80)
    
    def safe_numpy_to_tensor(numpy_array, dtype=None):
        """
        安全地将 NumPy 数组转换为 PyTorch 张量
        
        参数:
            numpy_array: NumPy 数组
            dtype: 目标数据类型（可选）
        
        返回:
            PyTorch 张量
        """
        # 确保是 NumPy 数组
        if not isinstance(numpy_array, np.ndarray):
            numpy_array = np.array(numpy_array)
        
        # 检查并修复可写性
        if not numpy_array.flags.writeable:
            numpy_array = numpy_array.copy()
        
        # 转换为张量
        if dtype is not None:
            return torch.tensor(numpy_array, dtype=dtype)
        else:
            return torch.from_numpy(numpy_array)
    
    print("\n函数定义:")
    print("-" * 80)
    import inspect
    print(inspect.getsource(safe_numpy_to_tensor))
    
    print("\n使用示例:")
    print("-" * 80)
    
    # 测试只读数组
    read_only_array = np.array([1, 2, 3], dtype=np.float32)
    read_only_array.setflags(write=False)
    
    print(f"   输入数组（只读）: {read_only_array}")
    print(f"   可写: {read_only_array.flags.writeable}")
    
    tensor = safe_numpy_to_tensor(read_only_array)
    print(f"   输出张量: {tensor}")
    print(f"   ✅ 转换成功，无警告")


def demonstrate_celery_integration():
    """演示 Celery 集成"""
    print("\n" + "=" * 80)
    print("Celery 任务中的使用")
    print("=" * 80)
    
    print("\n完整的任务示例:")
    print("-" * 80)
    print("""
  import numpy as np
  import torch
  from celery_app import app
  
  def safe_numpy_to_tensor(numpy_array):
      \"\"\"安全转换函数\"\"\"
      if not isinstance(numpy_array, np.ndarray):
          numpy_array = np.array(numpy_array)
      if not numpy_array.flags.writeable:
          numpy_array = numpy_array.copy()
      return torch.from_numpy(numpy_array)
  
  @app.task
  def process_model(data):
      # 获取 NumPy 数组
      numpy_array = result.as_numpy(model_config[self.model_name]["return_res"])
      
      # 安全转换为张量
      model_output = safe_numpy_to_tensor(numpy_array)
      
      # 继续处理
      return process(model_output)
    """)
    
    print("\nWorker 启动配置:")
    print("-" * 80)
    print("""
  # 使用 Eventlet 池避免多进程问题
  pip install eventlet
  
  celery -A ushow_nlp worker \\
      --loglevel=info \\
      --pool=eventlet \\
      --concurrency=50 \\
      --hostname=ai.ushow_nlp@%h \\
      --queues=ai.ushow_nlp
    """)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PyTorch/NumPy 警告修复演示")
    print("=" * 80)
    
    try:
        demonstrate_problem()
        demonstrate_solutions()
        demonstrate_actual_fix()
        demonstrate_safe_function()
        demonstrate_celery_integration()
        
        print("\n" + "=" * 80)
        print("✅ 演示完成！")
        print("=" * 80)
        print("\n💡 关键要点:")
        print("  1. 在转换前使用 copy() 确保数组可写")
        print("  2. 使用 Eventlet 池避免多进程问题")
        print("  3. 创建工具函数统一处理转换")
        print("  4. 详细说明请查看: PYTORCH_NUMPY_WARNING.md")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

