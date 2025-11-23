# Celery Group 实现深度解析

## 📋 目录

1. [Group 核心概念](#group-核心概念)
2. [Group 的实现原理](#group-的实现原理)
3. [Group 的数据结构](#group-的数据结构)
4. [Group 的执行流程](#group-的执行流程)
5. [并行执行机制](#并行执行机制)
6. [结果收集机制](#结果收集机制)
7. [源码级实现分析](#源码级实现分析)
8. [Group 的高级特性](#group-的高级特性)
9. [性能与限制](#性能与限制)
10. [Group vs Chain 对比](#group-vs-chain-对比)

---

## Group 核心概念

### 什么是 Group？

`group` 是 Celery 提供的一个**任务组合原语（Primitive）**，用于将多个**独立的任务并行执行**，所有任务完成后返回结果列表。

### 基本用法

```python
from celery import group

# 方式1: 使用 group() 函数
job = group(
    task1.s(arg1, arg2),
    task2.s(arg3, arg4),
    task3.s(arg5, arg6)
)

result = job.apply_async()
results = result.get()  # 返回 [result1, result2, result3]

# 方式2: 使用列表推导式
job = group(task.s(i) for i in range(10))
result = job.apply_async()
results = result.get()  # 返回包含 10 个结果的列表
```

### 执行流程示意

```
并行执行：
task1(arg1, arg2) ──┐
                     │
task2(arg3, arg4) ──┼──→ 所有任务完成后
                     │     返回结果列表
task3(arg5, arg6) ──┘     [result1, result2, result3]
```

---

## Group 的实现原理

### 1. Group 的本质

`group` 是一个**签名（Signature）对象**，它封装了多个独立任务的签名，这些任务可以并行执行。

### 2. Group 的创建过程

```python
# 当调用 group() 时，内部发生了什么？

from celery import group
from celery.canvas import _group

# group() 函数实际上是 _group() 的包装
job = group(
    fetch_data.s('source1'),
    fetch_data.s('source2'),
    fetch_data.s('source3')
)

# 等价于：
job = _group(
    fetch_data.s('source1'),
    fetch_data.s('source2'),
    fetch_data.s('source3')
)
```

### 3. Group 对象的结构

Group 对象内部维护了一个**任务签名列表**，每个任务都是独立的 Signature 对象：

```python
# 伪代码展示 Group 的内部结构
class Group:
    def __init__(self, *tasks):
        self.tasks = list(tasks)  # 存储任务签名列表
        self.app = tasks[0].app if tasks else None
        self.group_id = None  # Group ID，用于标识任务组
    
    def apply_async(self, **kwargs):
        # 并行提交所有任务
        ...
```

---

## Group 的数据结构

### Signature 对象

每个任务通过 `.s()` 方法创建 Signature（签名）对象：

```python
# task.s() 创建 Signature
signature = task.s(arg1, arg2, kwarg1=value1)

# Signature 包含的信息：
# - task: 任务函数
# - args: 位置参数
# - kwargs: 关键字参数
# - options: 执行选项（queue, routing_key, priority, group_id 等）
```

### Group 的序列化结构

当 Group 被序列化到消息队列时，其结构如下：

```json
{
    "task": "celery.group",
    "args": [],
    "kwargs": {
        "tasks": [
            {
                "task": "tasks.advanced_tasks.fetch_data",
                "args": ["source1"],
                "kwargs": {},
                "options": {
                    "group_id": "abc123..."  // 所有任务共享同一个 group_id
                }
            },
            {
                "task": "tasks.advanced_tasks.fetch_data",
                "args": ["source2"],
                "kwargs": {},
                "options": {
                    "group_id": "abc123..."  // 相同的 group_id
                }
            },
            {
                "task": "tasks.advanced_tasks.fetch_data",
                "args": ["source3"],
                "kwargs": {},
                "options": {
                    "group_id": "abc123..."  // 相同的 group_id
                }
            }
        ]
    }
}
```

### GroupResult 对象

Group 执行后返回 `GroupResult` 对象，用于跟踪和管理所有子任务的结果：

```python
# GroupResult 的结构
class GroupResult:
    def __init__(self, group_id, results):
        self.id = group_id  # Group ID
        self.results = results  # 子任务的 AsyncResult 列表
    
    def get(self, timeout=None, propagate=True):
        """获取所有任务的结果列表"""
        ...
    
    def successful(self):
        """检查是否所有任务都成功"""
        ...
    
    def failed(self):
        """检查是否有任务失败"""
        ...
```

---

## Group 的执行流程

### 完整执行流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 客户端调用 job.apply_async()                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Group.apply_async()                                      │
│    - 生成唯一的 group_id                                     │
│    - 为所有任务设置相同的 group_id                            │
│    - 创建 GroupResult 对象                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 并行发送所有任务到消息队列                                  │
│    - task1: {task_id: uuid1, group_id: "abc123"}            │
│    - task2: {task_id: uuid2, group_id: "abc123"}            │
│    - task3: {task_id: uuid3, group_id: "abc123"}           │
│    所有任务共享相同的 group_id                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 多个 Worker 并行接收和执行任务                             │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│    │ Worker 1 │  │ Worker 2 │  │ Worker 3 │                │
│    │ 执行task1│  │ 执行task2│  │ 执行task3│                │
│    └──────────┘  └──────────┘  └──────────┘                │
│         │              │              │                     │
│         └──────────────┴──────────────┘                     │
│                   并行执行                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 每个任务完成后，结果存储到结果后端                          │
│    - task1 结果 → Redis (task_id: uuid1)                    │
│    - task2 结果 → Redis (task_id: uuid2)                    │
│    - task3 结果 → Redis (task_id: uuid3)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 客户端通过 GroupResult.get() 获取所有结果                  │
│    - 根据 group_id 查找所有子任务的 task_id                   │
│    - 从结果后端读取每个任务的结果                              │
│    - 返回结果列表 [result1, result2, result3]               │
└──────────────────────────────────────────────────────────────┘
```

### 关键机制：Group ID

**Group ID 是 Group 实现的核心机制**。所有属于同一个 Group 的任务都共享相同的 `group_id`，用于：

1. **标识任务组**：将多个任务关联到同一个组
2. **结果收集**：通过 group_id 查找所有子任务的结果
3. **状态跟踪**：跟踪整个任务组的执行状态

```python
# 伪代码：Group 如何设置 group_id

def apply_async(self):
    # 生成唯一的 group_id
    group_id = uuid.uuid4().hex
    
    # 为所有任务设置相同的 group_id
    for task in self.tasks:
        task.options['group_id'] = group_id
    
    # 并行提交所有任务
    results = []
    for task in self.tasks:
        async_result = task.apply_async()
        results.append(async_result)
    
    # 创建 GroupResult
    return GroupResult(group_id, results)
```

---

## 并行执行机制

### 1. 任务如何并行执行？

Group 中的任务通过以下机制实现并行执行：

1. **独立任务提交**：每个任务都是独立提交到消息队列的
2. **Worker 并行处理**：多个 Worker 进程/线程可以同时处理不同的任务
3. **无依赖关系**：任务之间没有依赖，可以任意顺序执行

### 2. 并行执行的代码示例

```python
@app.task
def fetch_data(source):
    print(f"从 {source} 获取数据...")
    time.sleep(2)  # 模拟耗时操作
    return f"data_from_{source}"

# 创建 Group
job = group(
    fetch_data.s('source1'),
    fetch_data.s('source2'),
    fetch_data.s('source3')
)

# 执行 Group
result = job.apply_async()

# 执行时间线：
# T0: 所有任务同时提交到队列
# T1-T2: 三个 Worker 并行执行任务
# T2: 所有任务完成（总时间 ≈ 2秒，而不是 6秒）
```

### 3. Worker 并发模型

Group 的并行执行能力取决于 Worker 的并发模型：

#### Prefork（多进程）- 默认

```
Worker 主进程
├── 子进程 1 → 执行 task1
├── 子进程 2 → 执行 task2
├── 子进程 3 → 执行 task3
└── 子进程 4 → 空闲（等待新任务）

并行度 = Worker 并发数（默认 = CPU 核心数）
```

#### Eventlet/Gevent（协程）

```
Worker 主进程
├── 协程 1 → 执行 task1（I/O 等待时切换）
├── 协程 2 → 执行 task2（I/O 等待时切换）
├── 协程 3 → 执行 task3（I/O 等待时切换）
└── ...

并行度 = 协程数（可以设置到 100-1000）
```

### 4. 并行执行的优势

**时间对比**：

```python
# 串行执行（使用 Chain）
chain(
    task.s(1),  # 2秒
    task.s(2),  # 2秒
    task.s(3)   # 2秒
)
# 总时间：6秒

# 并行执行（使用 Group）
group(
    task.s(1),  # 2秒 ┐
    task.s(2),  # 2秒 ├─ 并行执行
    task.s(3)   # 2秒 ┘
)
# 总时间：2秒（假设有足够的 Worker）
```

---

## 结果收集机制

### 1. 结果如何收集？

Group 通过 `GroupResult` 对象收集所有子任务的结果：

```python
# GroupResult 收集结果的机制

class GroupResult:
    def get(self, timeout=None, propagate=True):
        """获取所有任务的结果列表"""
        results = []
        for async_result in self.results:
            try:
                result = async_result.get(timeout=timeout)
                results.append(result)
            except Exception as e:
                if propagate:
                    raise
                results.append(e)
        return results
```

### 2. 结果收集的流程

```
1. 客户端调用 result.get()
   ↓
2. GroupResult 遍历所有子任务的 AsyncResult
   ↓
3. 对每个 AsyncResult 调用 get()
   ↓
4. AsyncResult.get() 从结果后端（Redis）读取结果
   ↓
5. 收集所有结果，返回列表
```

### 3. 部分任务失败的处理

```python
# 默认行为：propagate=True，任何任务失败都会抛出异常
try:
    results = result.get(propagate=True)
except Exception as e:
    print(f"任务失败: {e}")

# 允许部分失败：propagate=False，返回结果列表（包含异常）
results = result.get(propagate=False)
# results = [result1, Exception(...), result3]
```

### 4. 结果顺序

**重要**：Group 返回的结果列表**保持任务定义的顺序**，而不是任务完成的顺序。

```python
job = group(
    slow_task.s(),   # 需要 5 秒
    fast_task.s(),   # 需要 1 秒
    medium_task.s()  # 需要 3 秒
)

result = job.apply_async()
results = result.get()

# results[0] = slow_task 的结果（即使它最后完成）
# results[1] = fast_task 的结果（即使它最先完成）
# results[2] = medium_task 的结果
```

---

## 源码级实现分析

### 1. Group 类的定义

Celery 的 Group 实现位于 `celery/canvas.py`：

```python
# celery/canvas.py (简化版)

class group(Signature):
    """Group 任务签名"""
    
    def __init__(self, *tasks, **options):
        # 将任务列表转换为 Signature 对象
        tasks = [maybe_signature(task) for task in tasks]
        
        # Group 本身不执行任务，只是封装任务列表
        super().__init__(
            'celery.group',  # 特殊任务类型
            args=(tasks,),   # 任务列表作为参数
            **options
        )
        
        self.tasks = tasks
    
    def apply_async(self, **kwargs):
        """异步执行 Group"""
        if not self.tasks:
            return GroupResult(None, [])
        
        # 生成唯一的 group_id
        group_id = uuid.uuid4().hex
        
        # 为所有任务设置相同的 group_id
        for task in self.tasks:
            task.options['group_id'] = group_id
        
        # 并行提交所有任务
        results = []
        for task in self.tasks:
            async_result = task.apply_async(**kwargs)
            results.append(async_result)
        
        # 创建并返回 GroupResult
        return GroupResult(group_id, results)
    
    def __or__(self, other):
        """支持 | 运算符（与 Chain 组合）"""
        return chain(self, other)
```

### 2. GroupResult 类的定义

```python
# celery/result.py (简化版)

class GroupResult:
    """Group 结果对象"""
    
    def __init__(self, group_id, results, backend=None):
        self.id = group_id
        self.results = results  # AsyncResult 列表
        self.backend = backend or current_app.backend
    
    def get(self, timeout=None, propagate=True):
        """获取所有任务的结果列表"""
        results = []
        for async_result in self.results:
            try:
                result = async_result.get(timeout=timeout)
                results.append(result)
            except Exception as e:
                if propagate:
                    raise
                results.append(e)
        return results
    
    def successful(self):
        """检查是否所有任务都成功"""
        return all(r.successful() for r in self.results)
    
    def failed(self):
        """检查是否有任务失败"""
        return any(r.failed() for r in self.results)
    
    def ready(self):
        """检查是否所有任务都完成"""
        return all(r.ready() for r in self.results)
```

### 3. 消息序列化

Group 在序列化时，会将所有任务签名包含在消息中：

```python
# celery/app/task.py (简化版)

def _build_message(self, task_id, args, kwargs, **options):
    """构建任务消息"""
    message = {
        'id': task_id,
        'task': self.name,
        'args': args,
        'kwargs': kwargs,
        'group_id': options.get('group_id'),  # Group ID
    }
    
    return message
```

### 4. Worker 执行 Group

当 Worker 接收到带有 `group_id` 的任务时：

```python
# celery/worker/request.py (简化版)

class Request:
    def execute(self):
        """执行任务"""
        # 执行任务
        result = self.task.run(*self.args, **self.kwargs)
        
        # 存储结果（包含 group_id 信息）
        self.task.backend.store_result(
            self.task_id,
            result,
            state='SUCCESS',
            group_id=self.request.get('group_id')  # 保存 group_id
        )
        
        return result
```

---

## Group 的高级特性

### 1. Group 与 Chain 的组合

Group 可以与 Chain 组合使用，实现复杂的工作流：

```python
from celery import chain, group

# 先执行一个任务，然后并行执行多个任务，最后聚合结果
workflow = chain(
    fetch_data.s('source'),
    group(
        process_item.s(),
        process_item.s(),
        process_item.s(),
    ),
    aggregate_results.s()
)

# 执行流程：
# 1. fetch_data('source') → 返回 data
# 2. 并行执行：
#    - process_item(data)
#    - process_item(data)
#    - process_item(data)
# 3. aggregate_results([result1, result2, result3]) → 最终结果
```

### 2. 动态 Group 创建

Group 支持动态创建，可以使用列表推导式：

```python
# 动态创建大量任务
job = group(
    process_item.s(i) for i in range(100)
)

# 或者
items = ['item1', 'item2', 'item3', ...]
job = group(
    process_item.s(item) for item in items
)
```

### 3. 部分结果获取

可以单独获取 Group 中某个任务的结果：

```python
result = job.apply_async()

# 获取所有结果
all_results = result.get()

# 获取第一个任务的结果
first_result = result.results[0].get()

# 获取特定任务的结果
specific_result = result.results[2].get()
```

### 4. 结果状态检查

```python
result = job.apply_async()

# 检查是否所有任务都完成
if result.ready():
    results = result.get()

# 检查是否所有任务都成功
if result.successful():
    results = result.get()

# 检查是否有任务失败
if result.failed():
    print("有任务失败")
```

### 5. 错误处理

```python
result = job.apply_async()

try:
    # propagate=True: 任何任务失败都会抛出异常
    results = result.get(propagate=True)
except Exception as e:
    print(f"任务失败: {e}")

# propagate=False: 返回结果列表，失败的任务返回异常对象
results = result.get(propagate=False)
for i, r in enumerate(results):
    if isinstance(r, Exception):
        print(f"任务 {i} 失败: {r}")
    else:
        print(f"任务 {i} 成功: {r}")
```

---

## 性能与限制

### 1. 性能特点

**优点**：
- ✅ **真正的并行执行**：任务可以在不同的 Worker 上同时执行
- ✅ **充分利用资源**：可以充分利用多核 CPU 和多个 Worker
- ✅ **时间效率**：总执行时间 ≈ 最慢任务的时间，而不是所有任务时间的总和

**缺点**：
- ❌ **资源消耗**：并行执行会消耗更多的 CPU、内存和网络资源
- ❌ **结果等待**：必须等待所有任务完成才能获取结果
- ❌ **无依赖控制**：无法控制任务之间的依赖关系

### 2. 使用场景

**适合使用 Group 的场景**：
- 独立任务：任务之间没有依赖关系
- 批量处理：需要处理大量独立的数据项
- 并行计算：需要充分利用多核 CPU
- 数据采集：从多个数据源并行获取数据

**不适合使用 Group 的场景**：
- 有依赖关系：任务之间有依赖关系（应使用 Chain）
- 需要顺序执行：必须按顺序执行的任务
- 资源受限：系统资源有限，无法支持并行执行

### 3. 最佳实践

```python
# ✅ 好的实践：任务之间没有依赖关系
job = group(
    fetch_data.s('source1'),  # 独立任务
    fetch_data.s('source2'),  # 独立任务
    fetch_data.s('source3')   # 独立任务
)

# ❌ 不好的实践：任务之间有依赖关系
job = group(
    fetch_data.s('source'),      # 需要先执行
    process_data.s(),            # 依赖 fetch_data 的结果
    save_data.s()               # 依赖 process_data 的结果
)
# 应该使用 Chain
```

### 4. 性能优化建议

1. **合理设置 Worker 并发数**：
   ```python
   # CPU 密集型：并发数 = CPU 核心数
   celery -A app worker --concurrency=4
   
   # I/O 密集型：可以使用更高的并发数
   celery -A app worker --pool=eventlet --concurrency=100
   ```

2. **使用合适的执行模型**：
   ```python
   # CPU 密集型：使用 prefork（默认）
   # I/O 密集型：使用 eventlet/gevent
   ```

3. **控制 Group 大小**：
   ```python
   # 避免创建过大的 Group（如 10000 个任务）
   # 可以分批处理
   for batch in chunks(items, 100):
       job = group(process_item.s(item) for item in batch)
       result = job.apply_async()
       results.extend(result.get())
   ```

---

## Group vs Chain 对比

### 核心差异

| 特性 | Group | Chain |
|------|-------|-------|
| **执行方式** | 并行执行 | 顺序执行 |
| **任务关系** | 独立，无依赖 | 有依赖，前一个任务的结果作为下一个任务的输入 |
| **执行时间** | 总时间 ≈ 最慢任务的时间 | 总时间 = 所有任务时间的总和 |
| **结果格式** | 结果列表 `[result1, result2, ...]` | 单个结果（最后一个任务的结果） |
| **适用场景** | 独立任务、批量处理 | 有依赖关系的任务流 |
| **资源消耗** | 高（并行执行） | 低（顺序执行） |

### 执行时间对比

```python
# 假设每个任务需要 2 秒

# Chain: 顺序执行
chain(task1.s(), task2.s(), task3.s())
# 总时间：2 + 2 + 2 = 6 秒

# Group: 并行执行
group(task1.s(), task2.s(), task3.s())
# 总时间：max(2, 2, 2) = 2 秒（假设有足够的 Worker）
```

### 组合使用

Group 和 Chain 可以组合使用，实现复杂的工作流：

```python
# 示例：ETL 流程
workflow = chain(
    extract_data.s('source'),        # 1. 提取数据
    group(                            # 2. 并行处理
        transform_data.s(),
        validate_data.s(),
        enrich_data.s(),
    ),
    load_data.s()                     # 3. 加载数据
)
```

---

## 总结

### Group 的核心要点

1. **并行执行**：Group 中的任务可以并行执行，充分利用系统资源
2. **Group ID**：所有任务共享相同的 group_id，用于结果收集和状态跟踪
3. **结果列表**：返回所有任务的结果列表，保持任务定义的顺序
4. **独立任务**：任务之间没有依赖关系，可以任意顺序执行

### Group 的实现精髓

Group 的实现非常巧妙：
- 它不是一个新的任务类型，而是**多个 Signature 的组合**
- 通过 **group_id** 将所有任务关联到同一个组
- 所有任务**独立提交**到消息队列，由 Worker 并行处理
- 通过 **GroupResult** 收集和管理所有子任务的结果

### 与其他原语的对比

| 特性 | Group | Chain | Chord |
|------|-------|-------|-------|
| 执行方式 | 并行 | 顺序 | 并行 + 回调 |
| 结果格式 | 列表 | 单个值 | 回调结果 |
| 适用场景 | 独立任务 | 有依赖的任务流 | 并行后聚合 |
| 执行时间 | 最慢任务时间 | 所有任务时间总和 | 最慢任务时间 + 回调时间 |

---

## 参考资料

- [Celery Canvas 文档](https://docs.celeryq.dev/en/stable/userguide/canvas.html)
- [Celery Group 源码](https://github.com/celery/celery/blob/main/celery/canvas.py)
- [任务组合原语](https://docs.celeryq.dev/en/stable/userguide/canvas.html#groups)

---

*文档创建时间：2024年*
*最后更新：2024年*

