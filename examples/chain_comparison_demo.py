"""
Chain 实现机制对比演示

这个脚本对比演示了 Celery Chain、LangChain Chain 和 LangGraph 的实现差异
注意：需要安装 langchain 和 langgraph 才能运行完整示例
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celery_app import app
from celery import chain
import time


# ============================================================================
# Celery Chain 示例
# ============================================================================

@app.task(name='tasks.chain_comparison.celery_step1')
def celery_step1(input_data):
    """Celery Chain 第一步"""
    print(f"[Celery Step1] 接收输入: {input_data}")
    print(f"[Celery Step1] 执行中... (异步执行，在 Worker 进程中)")
    time.sleep(1)  # 模拟处理时间
    result = f"celery_processed_{input_data}"
    print(f"[Celery Step1] 返回结果: {result}")
    return result


@app.task(name='tasks.chain_comparison.celery_step2')
def celery_step2(previous_result):
    """Celery Chain 第二步"""
    print(f"[Celery Step2] 接收上一步结果: {previous_result}")
    print(f"[Celery Step2] 执行中... (异步执行，在 Worker 进程中)")
    time.sleep(1)
    result = f"celery_enhanced_{previous_result}"
    print(f"[Celery Step2] 返回结果: {result}")
    return result


@app.task(name='tasks.chain_comparison.celery_step3')
def celery_step3(previous_result):
    """Celery Chain 第三步"""
    print(f"[Celery Step3] 接收上一步结果: {previous_result}")
    print(f"[Celery Step3] 执行中... (异步执行，在 Worker 进程中)")
    time.sleep(1)
    result = f"celery_final_{previous_result}"
    print(f"[Celery Step3] 返回最终结果: {result}")
    return result


def demonstrate_celery_chain():
    """演示 Celery Chain 的执行机制"""
    print("=" * 70)
    print("Celery Chain 执行机制演示")
    print("=" * 70)
    
    print("\n特点：")
    print("  - 异步执行：立即返回，不阻塞")
    print("  - 分布式执行：任务在 Worker 进程中执行")
    print("  - 结果传递：通过结果后端（Redis）传递")
    print("  - Link 机制：任务完成后自动触发下一个任务")
    
    print("\n创建 Chain:")
    workflow = chain(
        celery_step1.s('input_data'),
        celery_step2.s(),
        celery_step3.s()
    )
    
    print(f"  workflow: {workflow}")
    print(f"  workflow.tasks: {len(workflow.tasks)} 个任务")
    
    print("\n执行 Chain (异步):")
    print("  result = workflow.apply_async()  # 立即返回，不阻塞")
    result = workflow.apply_async()
    print(f"  返回 AsyncResult: {result.id}")
    
    print("\n等待结果 (阻塞):")
    print("  final_result = result.get(timeout=30)")
    try:
        final_result = result.get(timeout=30)
        print(f"  最终结果: {final_result}")
    except Exception as e:
        print(f"  执行失败: {e}")
    
    print("\n" + "-" * 70 + "\n")


# ============================================================================
# LangChain Chain 示例（需要安装 langchain）
# ============================================================================

def demonstrate_langchain_chain():
    """演示 LangChain Chain 的执行机制"""
    print("=" * 70)
    print("LangChain Chain 执行机制演示")
    print("=" * 70)
    
    try:
        from langchain_core.runnables import RunnablePassthrough
        
        print("\n特点：")
        print("  - 同步执行：阻塞直到完成")
        print("  - 主线程执行：在当前进程中执行")
        print("  - 结果传递：通过函数返回值传递")
        print("  - 函数组合：通过 | 运算符组合组件")
        
        # 定义组件
        def component1(inputs):
            print(f"[LangChain Component1] 接收输入: {inputs}")
            print(f"[LangChain Component1] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)  # 模拟处理时间
            result = f"langchain_processed_{inputs['data']}"
            print(f"[LangChain Component1] 返回结果: {result}")
            return {"data": result}
        
        def component2(inputs):
            print(f"[LangChain Component2] 接收上一步结果: {inputs}")
            print(f"[LangChain Component2] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)
            result = f"langchain_enhanced_{inputs['data']}"
            print(f"[LangChain Component2] 返回结果: {result}")
            return {"data": result}
        
        def component3(inputs):
            print(f"[LangChain Component3] 接收上一步结果: {inputs}")
            print(f"[LangChain Component3] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)
            result = f"langchain_final_{inputs['data']}"
            print(f"[LangChain Component3] 返回最终结果: {result}")
            return {"data": result}
        
        print("\n创建 Chain:")
        langchain_chain = (
            component1
            | component2
            | component3
        )
        print(f"  chain: {langchain_chain}")
        
        print("\n执行 Chain (同步，阻塞):")
        print("  result = chain.invoke({'data': 'input_data'})")
        result = langchain_chain.invoke({"data": "input_data"})
        print(f"  最终结果: {result}")
        
    except ImportError:
        print("\n⚠️  LangChain 未安装，跳过演示")
        print("   安装命令: pip install langchain langchain-core")
        print("\n模拟 LangChain Chain 的执行流程:")
        print("  1. component1.invoke() → 执行中（阻塞）")
        print("  2. component1 完成 → component2.invoke() → 执行中（阻塞）")
        print("  3. component2 完成 → component3.invoke() → 执行中（阻塞）")
        print("  4. component3 完成 → 返回结果")
    
    print("\n" + "-" * 70 + "\n")


# ============================================================================
# LangGraph 示例（需要安装 langgraph）
# ============================================================================

def demonstrate_langgraph():
    """演示 LangGraph 的执行机制"""
    print("=" * 70)
    print("LangGraph 执行机制演示")
    print("=" * 70)
    
    try:
        from typing import TypedDict
        from langgraph.graph import StateGraph, END
        
        print("\n特点：")
        print("  - 状态机模型：通过状态对象传递数据")
        print("  - 图结构：节点和边定义工作流")
        print("  - 条件分支：支持基于状态的条件路由")
        print("  - 循环控制：支持循环执行节点")
        
        # 定义状态
        class GraphState(TypedDict):
            data: str
            step: int
        
        # 定义节点
        def node1(state: GraphState) -> GraphState:
            print(f"[LangGraph Node1] 接收状态: {state}")
            print(f"[LangGraph Node1] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)
            state["data"] = f"langgraph_processed_{state['data']}"
            state["step"] = 1
            print(f"[LangGraph Node1] 更新状态: {state}")
            return state
        
        def node2(state: GraphState) -> GraphState:
            print(f"[LangGraph Node2] 接收状态: {state}")
            print(f"[LangGraph Node2] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)
            state["data"] = f"langgraph_enhanced_{state['data']}"
            state["step"] = 2
            print(f"[LangGraph Node2] 更新状态: {state}")
            return state
        
        def node3(state: GraphState) -> GraphState:
            print(f"[LangGraph Node3] 接收状态: {state}")
            print(f"[LangGraph Node3] 执行中... (同步执行，在主线程)")
            time.sleep(0.5)
            state["data"] = f"langgraph_final_{state['data']}"
            state["step"] = 3
            print(f"[LangGraph Node3] 更新状态: {state}")
            return state
        
        print("\n创建 Graph:")
        graph = StateGraph(GraphState)
        graph.add_node("node1", node1)
        graph.add_node("node2", node2)
        graph.add_node("node3", node3)
        graph.set_entry_point("node1")
        graph.add_edge("node1", "node2")
        graph.add_edge("node2", "node3")
        graph.add_edge("node3", END)
        
        print("  节点: node1 → node2 → node3 → END")
        
        print("\n编译 Graph:")
        app = graph.compile()
        print(f"  app: {app}")
        
        print("\n执行 Graph (同步，阻塞):")
        print("  result = app.invoke({'data': 'input_data', 'step': 0})")
        result = app.invoke({"data": "input_data", "step": 0})
        print(f"  最终状态: {result}")
        
    except ImportError:
        print("\n⚠️  LangGraph 未安装，跳过演示")
        print("   安装命令: pip install langgraph")
        print("\n模拟 LangGraph 的执行流程:")
        print("  1. 初始化状态对象: {'data': 'input_data', 'step': 0}")
        print("  2. 执行 node1 → 更新状态")
        print("  3. 根据边定义 → 执行 node2 → 更新状态")
        print("  4. 根据边定义 → 执行 node3 → 更新状态")
        print("  5. 到达 END → 返回最终状态")
    
    print("\n" + "-" * 70 + "\n")


# ============================================================================
# 对比总结
# ============================================================================

def print_comparison_summary():
    """打印对比总结"""
    print("=" * 70)
    print("Chain 实现机制对比总结")
    print("=" * 70)
    
    comparison = """
┌─────────────────────────────────────────────────────────────────────┐
│                     Celery  vs  LangChain  vs  LangGraph           │
├─────────────────────────────────────────────────────────────────────┤
│ 执行方式    │ 异步（立即返回）  │ 同步（阻塞等待）  │ 同步（阻塞等待） │
│ 执行位置    │ Worker 进程      │ 主线程           │ 主线程          │
│ 数据传递    │ 结果后端（Redis） │ 函数返回值        │ 状态对象        │
│ 控制流      │ 顺序执行         │ 顺序执行         │ 顺序/并行/条件   │
│ 错误处理    │ 任务级重试       │ 异常传播         │ 状态级处理      │
│ 持久化      │ 支持             │ 不支持           │ 不支持          │
│ 并发模型    │ 多进程/多线程    │ 单线程           │ 单线程          │
│ 适用场景    │ 后台任务、ETL    │ LLM 应用、RAG    │ 复杂工作流      │
└─────────────────────────────────────────────────────────────────────┘

关键差异：

1. 执行模型：
   - Celery: 异步分布式执行，适合长时间运行的任务
   - LangChain: 同步函数调用，适合快速处理
   - LangGraph: 同步状态机遍历，适合复杂工作流

2. 数据传递：
   - Celery: 通过持久化存储传递（适合分布式）
   - LangChain: 通过内存传递（适合快速处理）
   - LangGraph: 通过状态对象传递（适合复杂状态管理）

3. 控制流能力：
   - Celery/LangChain: 适合线性流程
   - LangGraph: 适合复杂工作流（条件分支、循环）

4. 选择建议：
   - 需要分布式执行 → Celery
   - 构建 LLM 应用 → LangChain
   - 需要复杂控制流 → LangGraph
"""
    print(comparison)
    print("=" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Chain 实现机制对比演示")
    print("=" * 70 + "\n")
    
    # 运行演示
    print_comparison_summary()
    
    print("\n⚠️  注意: Celery Chain 演示需要 Worker 正在运行")
    print("   请确保已启动 Worker: celery -A celery_app worker --loglevel=info\n")
    
    input("按 Enter 键继续 Celery Chain 演示...")
    demonstrate_celery_chain()
    
    input("按 Enter 键继续 LangChain Chain 演示...")
    demonstrate_langchain_chain()
    
    input("按 Enter 键继续 LangGraph 演示...")
    demonstrate_langgraph()
    
    print("\n" + "=" * 70)
    print("所有演示完成！")
    print("=" * 70 + "\n")
    print("详细对比分析请参考: doc/CHAIN_COMPARISON_CELERY_LANGCHAIN_LANGGRAPH.md")

