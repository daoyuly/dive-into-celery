# 🚀 Eventlet 池使用指南

## 📋 什么是 Eventlet？

Eventlet 是一个 Python 协程库，Celery 可以使用它作为 Worker 池类型。Eventlet 池使用协程（轻量级线程）而不是进程来执行任务。

---

## 🎯 为什么使用 Eventlet？

### 优势

1. **避免多进程问题**
   - ✅ 解决 SIGSEGV 错误
   - ✅ 解决 NumPy/PyTorch 多进程问题
   - ✅ 避免内存共享问题

2. **高并发性能**
   - ✅ 可以处理大量并发任务（100-1000+）
   - ✅ 适合 I/O 密集型任务
   - ✅ 内存占用小

3. **简单易用**
   - ✅ 安装简单
   - ✅ 配置简单
   - ✅ 兼容性好

### 适用场景

- ✅ **I/O 密集型任务**（网络请求、数据库查询、文件操作）
- ✅ **需要避免多进程问题的场景**（NumPy、PyTorch 等）
- ✅ **需要高并发的场景**
- ❌ **CPU 密集型任务**（受 GIL 限制，性能不如 prefork）

---

## 📦 安装

### 基本安装

```bash
# 使用 pip
pip install eventlet

# 使用 uv
uv pip install eventlet

# 指定版本
pip install eventlet==0.33.3
```

### 验证安装

```bash
python3 -c "import eventlet; print(eventlet.__version__)"
# 应该输出版本号，如: 0.33.3
```

---

## 🔧 配置和使用

### 方法 1: 启动参数（推荐）

```bash
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=50 \
    --loglevel=info \
    --hostname=worker@%h \
    --queues=basic,advanced,realworld
```

**关键参数**:
- `--pool=eventlet`: 使用 Eventlet 池
- `--concurrency=50`: 并发数（协程数），可以设置很高（50-1000+）

### 方法 2: 配置文件

```python
# celery_app.py
app.conf.update(
    worker_pool='eventlet',
    worker_concurrency=50,
)
```

### 方法 3: 环境变量

```bash
export CELERY_WORKER_POOL=eventlet
export CELERY_WORKER_CONCURRENCY=50

celery -A celery_app worker
```

---

## ⚙️ 配置参数

### 基本配置

```bash
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=50 \
    --loglevel=info \
    --hostname=worker@%h \
    --queues=basic
```

### 完整配置示例

```bash
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=100 \
    --loglevel=info \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240
```

### 参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `--pool=eventlet` | 使用 Eventlet 池 | 必需 |
| `--concurrency` | 并发数（协程数） | 50-1000（I/O 密集型） |
| `--loglevel` | 日志级别 | `info` 或 `debug` |
| `--hostname` | Worker 名称 | `worker@%h` |
| `--queues` | 监听的队列 | 根据需求 |
| `--max-tasks-per-child` | 每个协程执行的最大任务数 | 1000-5000 |
| `--time-limit` | 硬超时时间 | 300（秒） |
| `--soft-time-limit` | 软超时时间 | 240（秒） |

---

## 🎯 并发数设置

### 如何选择合适的并发数？

**I/O 密集型任务**:
```bash
# 网络请求、数据库查询、文件操作
--concurrency=100  # 可以设置很高
```

**混合任务**:
```bash
# 既有 I/O 又有计算
--concurrency=50   # 中等并发
```

**CPU 密集型任务**:
```bash
# 不推荐使用 eventlet，应该用 prefork
--pool=prefork --concurrency=4
```

### 并发数计算公式

```
并发数 = (预期 QPS / 单个任务耗时) × 缓冲系数

例如:
- 预期 QPS: 1000
- 单个任务耗时: 0.1 秒
- 缓冲系数: 1.5
- 并发数 = (1000 / 0.1) × 1.5 = 15000

实际建议: 50-500 之间，根据实际情况调整
```

---

## 📝 任务代码注意事项

### 1. 导入 Eventlet（如果需要）

```python
# 某些情况下需要 monkey patch
import eventlet
eventlet.monkey_patch()  # 让标准库支持协程
```

**注意**: Celery 会自动处理，通常不需要手动调用

### 2. 处理 NumPy/PyTorch

```python
import numpy as np
import torch

@app.task
def my_task(data):
    # Eventlet 池下，NumPy 数组通常是可写的
    # 但为了安全，仍然建议使用 copy()
    numpy_array = process_data(data)
    
    # 安全转换
    if not numpy_array.flags.writeable:
        numpy_array = numpy_array.copy()
    
    tensor = torch.from_numpy(numpy_array)
    return process(tensor)
```

### 3. 避免阻塞操作

```python
# ✅ 好的做法（使用协程友好的库）
import eventlet
import requests

@app.task
def my_task(url):
    # requests 在 eventlet 下会自动使用协程
    response = requests.get(url)
    return response.text

# ❌ 不好的做法（阻塞操作）
import time
@app.task
def my_task():
    time.sleep(10)  # 会阻塞所有协程
    # 应该使用: eventlet.sleep(10)
```

---

## 🔍 验证 Eventlet 是否工作

### 方法 1: 查看 Worker 启动日志

```bash
celery -A celery_app worker --pool=eventlet --concurrency=50
```

**应该看到**:
```
[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] celery@hostname ready.
[INFO/MainProcess] pidbox: Connected to redis://localhost:6379/0.
```

**不应该看到**:
```
[INFO/ForkPoolWorker-1] ...  # 这是 prefork 的日志
```

### 方法 2: 使用 Inspect

```python
from celery_app import app

inspect = app.control.inspect()
stats = inspect.stats()

for worker, worker_stats in stats.items():
    pool = worker_stats.get('pool', {})
    print(f"{worker}: {pool}")
    # 应该显示: {'implementation': 'eventlet'}
```

### 方法 3: 测试高并发

```python
from tasks.basic_tasks import add
from celery import group

# 提交 100 个任务
job = group(add.s(i, i) for i in range(100))
result = job.apply_async()

# Eventlet 池可以快速处理
print(result.get(timeout=10))
```

---

## ⚠️ 注意事项和限制

### 1. GIL 限制

**问题**:
- Python 的 GIL（全局解释器锁）仍然存在
- CPU 密集型任务无法真正并行

**影响**:
- Eventlet 不适合 CPU 密集型任务
- 适合 I/O 密集型任务

### 2. 库兼容性

**兼容的库**:
- ✅ `requests`（自动支持）
- ✅ `urllib3`（自动支持）
- ✅ 大多数标准库（通过 monkey patch）

**可能不兼容的库**:
- ⚠️ 某些 C 扩展库
- ⚠️ 某些阻塞的 C 库
- ⚠️ 某些多线程库

### 3. 调试困难

**问题**:
- 协程调试比进程调试困难
- 堆栈跟踪可能不完整

**建议**:
- 开发时使用 `solo` 池
- 生产环境使用 `eventlet` 池

### 4. 内存管理

**注意**:
- 虽然内存占用小，但仍需注意
- 设置 `--max-tasks-per-child` 防止内存泄漏

---

## 🆚 Eventlet vs Prefork vs Gevent

### 对比表

| 特性 | Eventlet | Prefork | Gevent |
|------|----------|---------|--------|
| **类型** | 协程 | 多进程 | 协程 |
| **并发数** | 50-1000+ | CPU 核心数 | 50-1000+ |
| **内存占用** | 低 | 高 | 低 |
| **CPU 密集型** | ❌ 差 | ✅ 最佳 | ❌ 差 |
| **I/O 密集型** | ✅ 最佳 | ⚠️ 一般 | ✅ 最佳 |
| **多进程问题** | ✅ 无 | ❌ 有 | ✅ 无 |
| **安装** | `pip install eventlet` | 内置 | `pip install gevent` |

### 选择建议

**使用 Eventlet**:
- I/O 密集型任务
- 需要避免多进程问题
- 需要高并发

**使用 Prefork**:
- CPU 密集型任务
- 需要进程隔离
- 多核服务器

**使用 Gevent**:
- I/O 密集型任务
- 与 Gevent 兼容的库
- 需要高并发

---

## 🔧 实际应用示例

### 示例 1: 基本使用

```bash
# 启动 Worker
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=50 \
    --loglevel=info \
    --queues=basic
```

### 示例 2: 生产环境配置

```bash
celery -A ushow_nlp worker \
    --pool=eventlet \
    --concurrency=100 \
    --loglevel=info \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240
```

### 示例 3: 开发环境配置

```bash
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=10 \
    --loglevel=debug \
    --queues=basic
```

### 示例 4: 高并发场景

```bash
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=500 \
    --loglevel=info \
    --queues=high_priority
```

---

## 🐛 常见问题

### 问题 1: 安装失败

```bash
# 错误: No module named 'eventlet'
pip install eventlet

# 如果还是失败，尝试:
pip install --upgrade pip
pip install eventlet
```

### 问题 2: 任务执行很慢

**可能原因**:
- 并发数设置太低
- 任务是 CPU 密集型的

**解决方案**:
```bash
# 增加并发数
--concurrency=100

# 或使用 prefork（如果是 CPU 密集型）
--pool=prefork --concurrency=4
```

### 问题 3: 内存占用高

**解决方案**:
```bash
# 设置更小的 max-tasks-per-child
--max-tasks-per-child=500

# 降低并发数
--concurrency=50
```

### 问题 4: 某些库不工作

**可能原因**:
- 库不支持协程
- 需要 monkey patch

**解决方案**:
```python
# 在任务开始时 monkey patch
import eventlet
eventlet.monkey_patch()

@app.task
def my_task():
    # 任务逻辑
    pass
```

---

## 📊 性能优化

### 1. 并发数优化

```bash
# 测试不同并发数的性能
for concurrency in 10 50 100 200; do
    celery -A celery_app worker --pool=eventlet --concurrency=$concurrency &
    # 运行测试
    # 记录性能指标
    pkill -f "celery.*worker"
done
```

### 2. 监控性能

```python
from celery_app import app

# 监控 Worker 状态
inspect = app.control.inspect()
stats = inspect.stats()

for worker, worker_stats in stats.items():
    pool = worker_stats.get('pool', {})
    total = worker_stats.get('total', {})
    print(f"{worker}:")
    print(f"  池类型: {pool.get('implementation', 'unknown')}")
    print(f"  成功任务: {total.get('tasks.succeeded', 0)}")
    print(f"  失败任务: {total.get('tasks.failed', 0)}")
```

### 3. 负载测试

```python
from tasks.basic_tasks import add
from celery import group
import time

# 提交大量任务
start = time.time()
job = group(add.s(i, i) for i in range(1000))
result = job.apply_async()
results = result.get(timeout=60)
elapsed = time.time() - start

print(f"处理 1000 个任务耗时: {elapsed:.2f} 秒")
print(f"QPS: {1000 / elapsed:.2f}")
```

---

## 🎓 最佳实践

### 1. 开发环境

```bash
# 使用较低的并发数，便于调试
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=10 \
    --loglevel=debug
```

### 2. 生产环境

```bash
# 使用较高的并发数，优化性能
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=100 \
    --loglevel=info \
    --max-tasks-per-child=1000
```

### 3. 高负载场景

```bash
# 使用非常高的并发数
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=500 \
    --loglevel=warning
```

### 4. 任务代码

```python
# ✅ 好的做法
@app.task
def my_task(url):
    import requests
    # requests 自动支持 eventlet
    response = requests.get(url)
    return response.text

# ✅ 处理 NumPy/PyTorch
@app.task
def my_task(data):
    import numpy as np
    numpy_array = process_data(data)
    if not numpy_array.flags.writeable:
        numpy_array = numpy_array.copy()
    return process(numpy_array)
```

---

## 📚 总结

### 快速开始

```bash
# 1. 安装
pip install eventlet

# 2. 启动 Worker
celery -A celery_app worker --pool=eventlet --concurrency=50

# 3. 提交任务
python3 examples/basic_usage.py
```

### 关键要点

1. **安装**: `pip install eventlet`
2. **启动**: `--pool=eventlet --concurrency=50`
3. **适用**: I/O 密集型任务，避免多进程问题
4. **并发**: 可以设置很高（50-1000+）
5. **注意**: 不适合 CPU 密集型任务

---

**Eventlet 是解决多进程问题和实现高并发的优秀选择！** 🚀

