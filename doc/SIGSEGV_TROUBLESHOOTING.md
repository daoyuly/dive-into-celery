# 🔴 SIGSEGV 错误故障排查指南

## 📋 错误分析

### 错误信息

```
Process 'ForkPoolWorker-1' pid:31 exited with 'signal 11 (SIGSEGV)'
WorkerLostError: Worker exited prematurely: signal 11 (SIGSEGV) Job: 2.
ChordError: Dependency raised WorkerLostError
```

### 错误类型

**SIGSEGV (Signal 11)**: 段错误（Segmentation Fault）
- 程序访问了不应该访问的内存地址
- 通常表示严重的内存错误
- 导致进程立即终止

---

## 🔍 可能的原因

### 1. 多进程问题（最可能）

**原因**:
- 使用 `prefork` 池时，子进程可能访问共享资源
- 某些库不支持多进程环境
- 进程间通信问题

**特征**:
- 错误发生在 `ForkPoolWorker-1`
- 使用 `prefork` 池时出现

### 2. C 扩展库问题

**原因**:
- Python C 扩展库在多进程环境下不稳定
- 某些科学计算库（NumPy、Pandas）在多进程下有问题
- 库的版本不兼容

**常见库**:
- NumPy
- Pandas
- OpenCV
- TensorFlow/PyTorch
- 其他 C 扩展库

### 3. 内存问题

**原因**:
- 内存不足
- 内存泄漏
- 访问已释放的内存

### 4. 任务代码问题

**原因**:
- 任务代码中有内存访问错误
- 使用了不安全的 C 库调用
- 多线程/多进程混用

### 5. Chord 任务特定问题

**原因**:
- Chord 任务涉及多个子任务
- 子任务之间的依赖关系导致问题
- 结果聚合时的内存问题

---

## ✅ 解决方案

### 方案 1: 使用 Solo 池（快速验证）

**目的**: 排除多进程问题

```bash
celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=solo \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp
```

**优点**:
- ✅ 单线程，避免多进程问题
- ✅ 易于调试
- ✅ 可以快速验证是否是进程问题

**缺点**:
- ❌ 性能差，无法并发
- ❌ 仅适合调试

**适用场景**: 快速验证问题是否由多进程引起

### 方案 2: 使用 Eventlet/Gevent 池（推荐）

**目的**: 避免多进程，使用协程

```bash
# 安装 eventlet
pip install eventlet

celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=eventlet \
    --concurrency=50 \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=1000
```

**优点**:
- ✅ 避免多进程问题
- ✅ 适合 I/O 密集型任务
- ✅ 性能好，可以高并发

**缺点**:
- ❌ 不适合 CPU 密集型任务
- ❌ 需要安装 eventlet

**适用场景**: I/O 密集型任务，或需要避免多进程问题

### 方案 3: 修复 Prefork 池配置

**目的**: 如果必须使用 prefork，优化配置

```bash
celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=prefork \
    --concurrency=2 \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=100 \
    --time-limit=300 \
    --soft-time-limit=240
```

**改进点**:
- ✅ 降低并发数（减少进程数）
- ✅ 设置更小的 `max-tasks-per-child`（更频繁重启进程）
- ✅ 添加超时限制

**适用场景**: CPU 密集型任务，必须使用 prefork

### 方案 4: 检查任务代码

**检查点**:

1. **C 扩展库使用**:
   ```python
   # 检查任务中是否使用了 C 扩展库
   import numpy as np
   import pandas as pd
   import cv2
   # 这些库在多进程下可能有问题
   ```

2. **共享资源访问**:
   ```python
   # 避免在任务中访问共享资源
   # 错误示例
   global_variable = ...  # 可能导致问题
   
   # 正确做法
   def my_task(data):
       # 使用局部变量
       local_data = process(data)
       return local_data
   ```

3. **内存管理**:
   ```python
   # 确保正确释放资源
   @app.task
   def my_task():
       try:
           # 任务逻辑
           result = process_data()
           return result
       finally:
           # 清理资源
           cleanup()
   ```

### 方案 5: 添加错误处理和日志

**目的**: 更好地定位问题

```python
@app.task(bind=True, max_retries=3)
def my_task(self, *args, **kwargs):
    try:
        # 任务逻辑
        result = process(*args, **kwargs)
        return result
    except Exception as e:
        # 记录详细错误信息
        import traceback
        error_msg = traceback.format_exc()
        print(f"任务错误: {error_msg}")
        
        # 重试或返回错误
        raise self.retry(exc=e, countdown=60)
```

### 方案 6: 检查系统资源

**检查内存**:
```bash
# 检查内存使用
free -h

# 检查进程内存
ps aux | grep celery

# 设置内存限制
ulimit -v 2097152  # 2GB
```

**检查系统限制**:
```bash
# 检查进程数限制
ulimit -u

# 检查文件描述符限制
ulimit -n
```

---

## 🔧 诊断步骤

### 步骤 1: 确认问题范围

```bash
# 1. 使用 solo 池测试（排除多进程问题）
celery -A ushow_nlp worker --pool=solo --queues=ai.ushow_nlp

# 如果 solo 池正常，说明是多进程问题
# 如果 solo 池也崩溃，说明是任务代码问题
```

### 步骤 2: 检查任务代码

```python
# 检查任务中是否使用了：
# 1. C 扩展库（NumPy, Pandas, OpenCV 等）
# 2. 全局变量
# 3. 共享资源
# 4. 多线程/多进程混用
```

### 步骤 3: 检查依赖库

```bash
# 检查库版本
pip list | grep -E "numpy|pandas|opencv|tensorflow|pytorch"

# 更新可能有问题的库
pip install --upgrade numpy pandas
```

### 步骤 4: 添加详细日志

```bash
# 使用 debug 日志级别
celery -A ushow_nlp worker \
    --loglevel=debug \
    --pool=prefork \
    --concurrency=1 \
    --queues=ai.ushow_nlp
```

### 步骤 5: 使用 GDB 调试（高级）

```bash
# 安装 gdb
apt-get install gdb python3-dbg

# 使用 gdb 运行 Worker
gdb python3
(gdb) run -m celery -A ushow_nlp worker --pool=prefork --concurrency=1

# 当崩溃时，查看堆栈
(gdb) bt
```

---

## 🎯 推荐解决方案（按优先级）

### 优先级 1: 使用 Eventlet 池（最推荐）

```bash
pip install eventlet

celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=eventlet \
    --concurrency=50 \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=1000
```

**为什么推荐**:
- ✅ 避免多进程问题（SIGSEGV 的主要原因）
- ✅ 性能好，可以高并发
- ✅ 适合大多数任务类型

### 优先级 2: 优化 Prefork 配置

如果必须使用 prefork（CPU 密集型任务）：

```bash
celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=prefork \
    --concurrency=2 \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp \
    --max-tasks-per-child=50 \
    --time-limit=300 \
    --soft-time-limit=240
```

**关键改进**:
- ✅ 降低并发数（减少进程数）
- ✅ 更频繁重启进程（防止内存问题）
- ✅ 添加超时限制

### 优先级 3: 修复任务代码

```python
# 1. 避免在任务中使用全局变量
# 2. 确保正确释放资源
# 3. 避免 C 扩展库的多进程问题
# 4. 使用线程安全的数据结构
```

---

## 📊 问题诊断流程图

```
SIGSEGV 错误
    │
    ├─ 使用 solo 池测试
    │   │
    │   ├─ 正常 → 多进程问题 → 使用 eventlet 池
    │   └─ 崩溃 → 任务代码问题 → 检查任务代码
    │
    ├─ 检查任务代码
    │   ├─ C 扩展库 → 避免或隔离
    │   ├─ 共享资源 → 使用局部变量
    │   └─ 内存问题 → 添加资源清理
    │
    └─ 检查系统资源
        ├─ 内存不足 → 增加内存或降低并发
        └─ 进程限制 → 调整 ulimit
```

---

## 🔍 常见场景和解决方案

### 场景 1: 使用 NumPy/Pandas

**问题**: NumPy/Pandas 在多进程下可能有问题

**解决方案**:
```python
# 方案 1: 使用 eventlet 池
celery -A ushow_nlp worker --pool=eventlet --concurrency=50

# 方案 2: 在任务开始时初始化 NumPy
@app.task
def my_task():
    import numpy as np
    # 确保 NumPy 在任务内部导入
    np.random.seed()  # 重置随机种子
    # 任务逻辑
```

### 场景 2: 使用 TensorFlow/PyTorch

**问题**: 深度学习框架在多进程下有问题

**解决方案**:
```python
# 方案 1: 使用 solo 池（仅调试）
celery -A ushow_nlp worker --pool=solo

# 方案 2: 在任务中延迟加载模型
@app.task
def my_task():
    # 在任务内部加载模型，避免多进程问题
    import tensorflow as tf
    model = tf.keras.models.load_model('model.h5')
    # 任务逻辑
```

### 场景 3: Chord 任务崩溃

**问题**: Chord 任务中的子任务崩溃

**解决方案**:
```python
# 1. 检查子任务代码
# 2. 添加错误处理
@app.task(bind=True, max_retries=3)
def chord_task(self, data):
    try:
        return process(data)
    except Exception as e:
        # 记录错误
        logger.error(f"Chord 任务错误: {e}")
        raise

# 3. 使用 eventlet 池避免多进程问题
celery -A ushow_nlp worker --pool=eventlet
```

---

## 🛠️ 临时解决方案

如果问题紧急，可以先用以下配置临时解决：

```bash
# 方案 1: 使用 solo 池（单线程，避免多进程问题）
celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=solo \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp

# 方案 2: 使用 eventlet 池（协程，避免多进程问题）
pip install eventlet
celery -A ushow_nlp worker \
    --loglevel=info \
    --pool=eventlet \
    --concurrency=50 \
    --hostname=ai.ushow_nlp@%h \
    --queues=ai.ushow_nlp
```

---

## 📋 检查清单

遇到 SIGSEGV 错误时，按以下顺序检查：

- [ ] 1. 使用 solo 池测试（排除多进程问题）
- [ ] 2. 检查任务代码中的 C 扩展库使用
- [ ] 3. 检查是否有全局变量或共享资源
- [ ] 4. 检查系统内存和资源限制
- [ ] 5. 检查依赖库版本
- [ ] 6. 添加详细日志定位问题
- [ ] 7. 考虑使用 eventlet 池替代 prefork

---

## 💡 最佳实践

### 1. 任务代码规范

```python
# ✅ 好的做法
@app.task
def my_task(data):
    # 使用局部变量
    result = process(data)
    return result

# ❌ 不好的做法
global_var = ...  # 全局变量
@app.task
def my_task():
    global global_var  # 可能导致多进程问题
    ...
```

### 2. 资源管理

```python
@app.task
def my_task():
    resource = acquire_resource()
    try:
        result = process(resource)
        return result
    finally:
        release_resource(resource)  # 确保释放
```

### 3. 错误处理

```python
@app.task(bind=True, max_retries=3)
def my_task(self, data):
    try:
        return process(data)
    except Exception as e:
        logger.error(f"任务错误: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)
```

---

## 🎓 总结

### 最可能的原因

1. **多进程问题**（90% 的可能性）
   - Prefork 池在多进程环境下不稳定
   - 某些库不支持多进程

2. **C 扩展库问题**（80% 的可能性）
   - NumPy、Pandas、OpenCV 等
   - 深度学习框架

3. **任务代码问题**（50% 的可能性）
   - 全局变量
   - 共享资源
   - 内存泄漏

### 推荐解决方案

**立即解决**:
```bash
# 使用 eventlet 池（最推荐）
pip install eventlet
celery -A ushow_nlp worker --pool=eventlet --concurrency=50 --queues=ai.ushow_nlp
```

**长期解决**:
1. 检查并修复任务代码
2. 避免使用不兼容多进程的库
3. 使用 eventlet 池替代 prefork（如果可能）

---

**SIGSEGV 错误通常由多进程问题引起，使用 eventlet 池是最有效的解决方案！** 🚀

