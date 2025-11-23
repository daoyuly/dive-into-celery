"""
Chain 实现机制演示

这个脚本深入演示了 Celery Chain 的内部工作机制，包括：
1. Chain 的创建过程
2. Link 回调的设置
3. 结果传递机制
4. Chain 的序列化结构
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from celery import chain
from celery.canvas import Signature
import json


@app.task(name='tasks.chain_demo.step1')
def step1(input_data):
    """第一步：处理输入数据"""
    print(f"[Step1] 接收输入: {input_data}")
    result = f"processed_{input_data}"
    print(f"[Step1] 返回结果: {result}")
    return result


@app.task(name='tasks.chain_demo.step2')
def step2(previous_result):
    """第二步：处理上一步的结果"""
    print(f"[Step2] 接收上一步结果: {previous_result}")
    result = f"enhanced_{previous_result}"
    print(f"[Step2] 返回结果: {result}")
    return result


@app.task(name='tasks.chain_demo.step3')
def step3(previous_result):
    """第三步：最终处理"""
    print(f"[Step3] 接收上一步结果: {previous_result}")
    result = f"final_{previous_result}"
    print(f"[Step3] 返回最终结果: {result}")
    return result


def demonstrate_chain_creation():
    """演示 Chain 的创建过程"""
    print("=" * 70)
    print("演示1: Chain 的创建过程")
    print("=" * 70)
    
    # 创建任务签名
    sig1 = step1.s('input_data')
    sig2 = step2.s()
    sig3 = step3.s()
    
    print("\n1. 创建任务签名:")
    print(f"   sig1: {sig1}")
    print(f"   sig2: {sig2}")
    print(f"   sig3: {sig3}")
    
    # 创建 Chain
    workflow = chain(sig1, sig2, sig3)
    
    print("\n2. 创建 Chain:")
    print(f"   workflow: {workflow}")
    print(f"   workflow.tasks: {workflow.tasks}")
    
    # 检查 link 设置
    print("\n3. 检查 Link 设置:")
    for i, task in enumerate(workflow.tasks):
        print(f"   Task {i+1} ({task.task}):")
        if 'link' in task.options:
            print(f"      link: {task.options['link']}")
        else:
            print(f"      link: None (最后一个任务)")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_chain_serialization():
    """演示 Chain 的序列化结构"""
    print("=" * 70)
    print("演示2: Chain 的序列化结构")
    print("=" * 70)
    
    workflow = chain(
        step1.s('input_data'),
        step2.s(),
        step3.s()
    )
    
    # 获取第一个任务的序列化信息
    first_task = workflow.tasks[0]
    serialized = first_task.as_dict()
    
    print("\n第一个任务的序列化结构:")
    print(json.dumps(serialized, indent=2, ensure_ascii=False))
    
    # 检查 link 信息
    if 'link' in first_task.options:
        print("\nLink 回调信息:")
        for i, link_task in enumerate(first_task.options['link']):
            print(f"\n  Link {i+1}:")
            link_dict = link_task.as_dict()
            print(json.dumps(link_dict, indent=4, ensure_ascii=False))
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_chain_execution():
    """演示 Chain 的执行过程"""
    print("=" * 70)
    print("演示3: Chain 的执行过程")
    print("=" * 70)
    
    print("\n执行 Chain:")
    print("  chain(step1.s('input_data'), step2.s(), step3.s())")
    print("\n预期执行流程:")
    print("  1. step1('input_data') → 返回 'processed_input_data'")
    print("  2. step2('processed_input_data') → 返回 'enhanced_processed_input_data'")
    print("  3. step3('enhanced_processed_input_data') → 返回 'final_enhanced_processed_input_data'")
    
    workflow = chain(
        step1.s('input_data'),
        step2.s(),
        step3.s()
    )
    
    print("\n提交任务链...")
    result = workflow.apply_async()
    print(f"任务链 ID: {result.id}")
    print("\n等待执行结果...")
    
    try:
        final_result = result.get(timeout=30)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_result_passing():
    """演示结果传递机制"""
    print("=" * 70)
    print("演示4: 结果传递机制")
    print("=" * 70)
    
    @app.task(name='tasks.chain_demo.return_tuple')
    def return_tuple():
        """返回元组，演示多参数传递"""
        result = (1, 2, 3)
        print(f"[return_tuple] 返回元组: {result}")
        return result
    
    @app.task(name='tasks.chain_demo.receive_multiple')
    def receive_multiple(x, y, z):
        """接收多个参数"""
        result = x + y + z
        print(f"[receive_multiple] 接收参数: x={x}, y={y}, z={z}")
        print(f"[receive_multiple] 计算结果: {result}")
        return result
    
    print("\n演示元组解包传递:")
    print("  return_tuple() → (1, 2, 3)")
    print("  receive_multiple(1, 2, 3) → 6")
    
    workflow = chain(
        return_tuple.s(),
        receive_multiple.s()
    )
    
    print("\n提交任务链...")
    result = workflow.apply_async()
    
    try:
        final_result = result.get(timeout=30)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_partial_arguments():
    """演示部分参数传递"""
    print("=" * 70)
    print("演示5: 部分参数传递")
    print("=" * 70)
    
    @app.task(name='tasks.chain_demo.base_task')
    def base_task():
        """基础任务，返回一个值"""
        result = 10
        print(f"[base_task] 返回: {result}")
        return result
    
    @app.task(name='tasks.chain_demo.multiply_task')
    def multiply_task(value, multiplier):
        """乘法任务，接收两个参数"""
        result = value * multiplier
        print(f"[multiply_task] 接收: value={value}, multiplier={multiplier}")
        print(f"[multiply_task] 计算结果: {result}")
        return result
    
    print("\n演示部分参数传递:")
    print("  base_task() → 10")
    print("  multiply_task(10, multiplier=5) → 50")
    print("\n注意: base_task 的结果作为第一个参数，multiplier 是固定参数")
    
    workflow = chain(
        base_task.s(),
        multiply_task.s(multiplier=5)  # 部分参数
    )
    
    print("\n提交任务链...")
    result = workflow.apply_async()
    
    try:
        final_result = result.get(timeout=30)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_chain_with_group():
    """演示 Chain 与 Group 的组合"""
    print("=" * 70)
    print("演示6: Chain 与 Group 的组合")
    print("=" * 70)
    
    from celery import group
    
    @app.task(name='tasks.chain_demo.fetch_data')
    def fetch_data(source):
        """获取数据"""
        data = [f"item_{i}" for i in range(3)]
        print(f"[fetch_data] 从 {source} 获取数据: {data}")
        return data
    
    @app.task(name='tasks.chain_demo.process_item')
    def process_item(item):
        """处理单个项目"""
        result = f"processed_{item}"
        print(f"[process_item] 处理 {item} → {result}")
        return result
    
    @app.task(name='tasks.chain_demo.aggregate')
    def aggregate(results):
        """聚合结果"""
        print(f"[aggregate] 聚合 {len(results)} 个结果: {results}")
        return f"aggregated_{len(results)}_items"
    
    print("\n工作流:")
    print("  1. fetch_data('source') → 返回列表")
    print("  2. 并行处理列表中的每个项目 (Group)")
    print("  3. aggregate(所有处理结果) → 最终结果")
    
    workflow = chain(
        fetch_data.s('source'),
        group(
            process_item.s(),
            process_item.s(),
            process_item.s(),
        ),
        aggregate.s()
    )
    
    print("\n提交复杂工作流...")
    result = workflow.apply_async()
    
    try:
        final_result = result.get(timeout=60)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


def demonstrate_chain_operator():
    """演示管道运算符 | 的使用"""
    print("=" * 70)
    print("演示7: 管道运算符 | 的使用")
    print("=" * 70)
    
    print("\n使用 | 运算符创建 Chain:")
    print("  workflow = step1.s('input') | step2.s() | step3.s()")
    print("\n等价于:")
    print("  workflow = chain(step1.s('input'), step2.s(), step3.s())")
    
    # 使用管道运算符
    workflow = step1.s('input') | step2.s() | step3.s()
    
    print(f"\n创建的 workflow: {workflow}")
    print(f"workflow 类型: {type(workflow)}")
    
    print("\n提交任务链...")
    result = workflow.apply_async()
    
    try:
        final_result = result.get(timeout=30)
        print(f"\n✅ 最终结果: {final_result}")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Celery Chain 实现机制深度演示")
    print("=" * 70 + "\n")
    
    # 运行演示
    demonstrate_chain_creation()
    demonstrate_chain_serialization()
    
    print("\n⚠️  注意: 以下演示需要 Worker 正在运行")
    print("   请确保已启动 Worker: celery -A celery_app worker --loglevel=info\n")
    
    input("按 Enter 键继续执行任务链演示...")
    
    demonstrate_chain_execution()
    demonstrate_result_passing()
    demonstrate_partial_arguments()
    demonstrate_chain_with_group()
    demonstrate_chain_operator()
    
    print("\n" + "=" * 70)
    print("所有演示完成！")
    print("=" * 70 + "\n")

