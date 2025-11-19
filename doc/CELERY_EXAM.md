# 📝 Celery 综合能力考试

**考试时间**: 120 分钟  
**总分**: 100 分  
**难度**: 中等偏难

---

## 📋 考试说明

本考试旨在全面评估你对 Celery 的理解和应用能力，包括：
- 基础概念和架构
- 进程模型和执行机制
- 任务分配和路由
- 配置和优化
- 实际应用场景
- 故障排查能力

**评分标准**:
- 90-100 分: 优秀（深入理解，能解决复杂问题）
- 80-89 分: 良好（理解核心概念，能处理常见问题）
- 70-79 分: 及格（掌握基础知识，需要进一步学习）
- <70 分: 需要重新学习

---

## 第一部分：选择题（每题 2 分，共 20 分）

### 1. Celery 默认使用的执行模型是？

A. 多线程（Threading）  
B. 多进程（Prefork）  
C. 协程（Eventlet）  
D. 单线程（Solo）

**答案**: B

---

### 2. 在 Prefork 模式下，任务在哪个进程中执行？

A. 主进程  
B. 子进程  
C. 主进程和子进程都可以  
D. 取决于配置

**答案**: B

---

### 3. 以下哪个 Pool 模式适合 I/O 密集型任务？

A. Prefork  
B. Solo  
C. Eventlet  
D. 以上都可以

**答案**: C

---

### 4. 在 Prefork 模式下，任务是如何分配到不同子进程的？

A. 主进程从队列获取任务，然后分配给子进程  
B. 每个子进程独立从队列竞争获取任务  
C. 主进程轮询分配任务给子进程  
D. 由操作系统调度分配

**答案**: B

---

### 5. `worker_prefetch_multiplier=4` 且 `--concurrency=4`，总预取数是多少？

A. 4  
B. 8  
C. 16  
D. 64

**答案**: C（4 × 4 = 16）

---

### 6. 以下哪个配置适合 CPU 密集型任务？

A. `--pool=prefork --concurrency=100`  
B. `--pool=eventlet --concurrency=4`  
C. `--pool=prefork --concurrency=4`  
D. `--pool=solo --concurrency=4`

**答案**: C

---

### 7. 任务路由配置中，`'tasks.email.*'` 中的 `*` 表示？

A. 所有任务  
B. 该模块下的所有任务  
C. 所有以 email 开头的任务  
D. 通配符，匹配任意字符

**答案**: B

---

### 8. 在 Prefork 模式下，每个子进程的 Redis 连接是？

A. 共享主进程的连接  
B. 每个子进程有独立的连接  
C. 使用连接池共享  
D. 取决于配置

**答案**: B

---

### 9. 写时复制（COW）机制的主要优势是？

A. 提高任务执行速度  
B. 减少内存占用  
C. 提高进程创建速度  
D. B 和 C

**答案**: D

---

### 10. 以下哪个命令可以启动一个监听 basic 和 advanced 队列的 Worker？

A. `celery -A celery_app worker --queues=basic,advanced`  
B. `celery -A celery_app worker --queue=basic --queue=advanced`  
C. `celery -A celery_app worker -Q basic,advanced`  
D. A 和 C 都可以

**答案**: D

---

## 第二部分：填空题（每空 2 分，共 20 分）

### 1. Celery 的三大核心组件是：**消息代理（Broker）**、**结果后端（Backend）** 和 **Worker**。

### 2. 在 Prefork 模式下，如果 `--concurrency=4`，系统会有 **1** 个主进程和 **4** 个子进程。

### 3. 预取数的计算公式是：**预取数 = worker_prefetch_multiplier × concurrency**。

### 4. Celery 使用 **BRPOP**（阻塞式右弹出）命令从 Redis 队列获取任务，这是一个**原子操作**，确保每个任务只被一个进程获取。

### 5. 在 Prefork 模式下，主进程负责**进程管理**、**信号处理**和**日志聚合**，不参与任务执行。

### 6. 任务序列化格式推荐使用 **JSON**，避免使用 **pickle**（因为安全风险）。

### 7. 在 Eventlet 模式下，所有协程在**同一个进程**、**同一个线程**中运行，通过**协程切换**实现并发。

### 8. `--max-tasks-per-child=1000` 的作用是**防止内存泄漏**，每个子进程执行 1000 个任务后会被重启。

### 9. 任务路由配置中，路由规则按**顺序匹配**，**第一个匹配的规则**生效。

### 10. 在 Prefork 模式下，子进程通过 **fork()** 系统调用创建，使用**写时复制（COW）**机制优化内存使用。

---

## 第三部分：判断题（每题 2 分，共 10 分）

### 1. Celery 默认使用多线程执行任务。

**答案**: ❌ 错误（默认使用多进程 Prefork）

---

### 2. 在 Prefork 模式下，主进程会参与任务的执行。

**答案**: ❌ 错误（主进程只负责管理，不执行任务）

---

### 3. 预取机制总是能提高性能，应该设置得越大越好。

**答案**: ❌ 错误（预取数过大会导致负载不均衡）

---

### 4. 在 Prefork 模式下，每个子进程有独立的 Redis 连接。

**答案**: ✅ 正确

---

### 5. Solo 模式适合生产环境使用。

**答案**: ❌ 错误（Solo 模式仅用于调试）

---

## 第四部分：简答题（每题 5 分，共 20 分）

### 1. 请解释 Prefork 模式和 Eventlet 模式的主要区别，以及各自的适用场景。

**参考答案**:

**Prefork 模式**:
- 使用多进程，每个任务在独立进程中执行
- 真正并行，可以充分利用多核 CPU
- 进程隔离，一个任务崩溃不影响其他任务
- 内存占用较大（每个进程独立内存）
- **适用场景**: CPU 密集型任务（计算、图像处理等）

**Eventlet 模式**:
- 使用协程，所有任务在同一个进程的协程中执行
- 通过协程切换实现并发（非真正并行）
- 内存占用较小
- 受 GIL 限制，不适合 CPU 密集型任务
- **适用场景**: I/O 密集型任务（网络请求、文件操作等）

---

### 2. 请解释任务分配机制：为什么说"不是分配，而是竞争获取"？

**参考答案**:

- **不是分配**: 主进程不会从队列获取任务然后分配给子进程
- **竞争获取**: 每个子进程独立连接 Redis，使用 `BRPOP` 命令从队列竞争获取任务
- **原子操作**: `BRPOP` 是原子操作，Redis 保证每个任务只被一个进程获取
- **优势**: 避免了主进程成为瓶颈，提高了并发性能

---

### 3. 请解释预取机制的工作原理，以及如何选择合适的预取数。

**参考答案**:

**工作原理**:
- 每个子进程在空闲时，提前从队列获取多个任务到本地缓冲区
- 预取数 = `worker_prefetch_multiplier × concurrency`
- 子进程执行任务时，优先从本地缓冲区获取

**选择策略**:
- **CPU 密集型任务**: 较小的预取数（1-2），避免负载不均衡
- **I/O 密集型任务**: 较大的预取数（10+），提高吞吐量
- **混合任务**: 中等预取数（4-6）

---

### 4. 请解释写时复制（COW）机制在 Prefork 模式下的作用。

**参考答案**:

**COW 机制**:
- 子进程创建时，不立即复制父进程的内存
- 父子进程共享同一份物理内存页（只读）
- 只有当某个进程写入内存页时，才真正复制该页

**优势**:
- 创建子进程非常快（只需复制页表）
- 内存占用最小（共享只读数据）
- 代码段和只读数据在所有进程中共享

**共享的数据**:
- 代码段（Python 字节码、库代码）
- 常量、字符串字面量
- 导入的模块代码（只读部分）

**独立的数据**:
- 堆内存（任务执行时创建的对象）
- 栈内存（函数调用、局部变量）
- 网络连接、数据库连接

---

## 第五部分：编程题（每题 10 分，共 20 分）

### 1. 请编写一个 Celery 任务，实现以下功能：

- 任务名称: `tasks.data_processing.process_data`
- 功能: 处理数据列表，计算每个元素的平方
- 要求: 
  - 支持进度更新（使用 `update_state`）
  - 支持重试（最多 3 次）
  - 设置超时时间（60 秒）

**参考答案**:

```python
from celery_app import app
import time

@app.task(
    name='tasks.data_processing.process_data',
    bind=True,
    max_retries=3,
    time_limit=60,
    soft_time_limit=55
)
def process_data(self, data_list):
    """
    处理数据列表，计算每个元素的平方
    
    Args:
        data_list: 数据列表
        self: 任务实例（bind=True 时自动传入）
    
    Returns:
        处理后的数据列表
    """
    try:
        result = []
        total = len(data_list)
        
        for i, item in enumerate(data_list):
            # 计算平方
            squared = item ** 2
            result.append(squared)
            
            # 更新进度
            progress = (i + 1) / total * 100
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total,
                    'progress': progress
                }
            )
            
            # 模拟处理时间
            time.sleep(0.1)
        
        return result
    
    except Exception as exc:
        # 重试
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

---

### 2. 请编写一个任务路由配置，实现以下需求：

- `tasks.critical.*` 任务路由到 `critical` 队列，优先级 9
- `tasks.normal.*` 任务路由到 `normal` 队列，优先级 5
- `tasks.low.*` 任务路由到 `low` 队列，优先级 1
- 其他任务路由到 `default` 队列

**参考答案**:

```python
# celery_app.py
app.conf.update(
    task_routes={
        'tasks.critical.*': {
            'queue': 'critical',
            'priority': 9,
        },
        'tasks.normal.*': {
            'queue': 'normal',
            'priority': 5,
        },
        'tasks.low.*': {
            'queue': 'low',
            'priority': 1,
        },
        '*': {
            'queue': 'default',
        },
    },
    task_default_queue='default',
    task_default_priority=5,
)
```

---

## 第六部分：场景分析题（每题 10 分，共 20 分）

### 1. 场景：生产环境性能问题

**问题描述**:
- 生产环境使用 Prefork 模式，`--concurrency=4`
- 有 1000 个任务需要处理
- 发现任务执行很慢，CPU 使用率只有 25%
- 内存使用率正常

**问题分析**:
1. 可能的原因是什么？
2. 如何优化？

**参考答案**:

**问题分析**:
1. **任务类型不匹配**: 可能是 I/O 密集型任务，但使用了 Prefork 模式
2. **并发数不足**: `--concurrency=4` 可能不够
3. **预取数过大**: 可能导致负载不均衡
4. **任务执行时间差异大**: 某些任务执行慢，阻塞了其他任务

**优化方案**:

**方案 1: 切换到 Eventlet 模式（如果是 I/O 密集型）**
```bash
pip install eventlet

celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=100 \
    --queues=basic,advanced,realworld
```

**方案 2: 增加并发数（如果是 CPU 密集型）**
```bash
celery -A celery_app worker \
    --pool=prefork \
    --concurrency=8 \
    --queues=basic,advanced,realworld
```

**方案 3: 调整预取数**
```python
app.conf.update(
    worker_prefetch_multiplier=1,  # 减小预取数，提高负载均衡
)
```

**方案 4: 任务分类处理**
```bash
# CPU 密集型任务
celery -A celery_app worker \
    --pool=prefork \
    --concurrency=4 \
    --queues=cpu

# I/O 密集型任务
celery -A celery_app worker \
    --pool=eventlet \
    --concurrency=100 \
    --queues=io
```

---

### 2. 场景：任务分配不均衡

**问题描述**:
- 使用 Prefork 模式，`--concurrency=4`，`worker_prefetch_multiplier=10`
- 发现子进程 1 和 2 很忙，子进程 3 和 4 很空闲
- 队列中还有很多任务等待处理

**问题分析**:
1. 可能的原因是什么？
2. 如何解决？

**参考答案**:

**问题分析**:
1. **预取数过大**: `worker_prefetch_multiplier=10` 导致每个子进程预取 10 个任务
2. **任务执行时间差异**: 子进程 1 和 2 可能获取了执行时间长的任务
3. **负载不均衡**: 快的进程预取了更多任务，慢的进程空闲

**解决方案**:

**方案 1: 减小预取数**
```python
app.conf.update(
    worker_prefetch_multiplier=1,  # 或 2
)
```

**方案 2: 使用公平分发**
```python
app.conf.update(
    worker_prefetch_multiplier=1,
    task_acks_late=True,  # 任务完成后才确认
)
```

**方案 3: 任务分类**
- 将执行时间长的任务和短任务分开到不同队列
- 为不同队列配置不同的 Worker

**方案 4: 监控和调整**
- 使用 Flower 监控任务执行时间
- 根据实际情况调整预取数和并发数

---

## 第七部分：故障排查题（10 分）

### 场景：Worker 无法获取任务

**问题描述**:
- Worker 启动正常，日志显示连接 Redis 成功
- 队列中有任务，但 Worker 无法获取
- 使用 `celery -A celery_app inspect active` 显示没有活动任务

**可能的原因和解决方案**:

**参考答案**:

**可能原因 1: 队列名称不匹配**
```bash
# 检查 Worker 监听的队列
celery -A celery_app inspect active_queues

# 检查任务路由配置
# 确保任务路由到的队列与 Worker 监听的队列一致
```

**解决方案**:
```bash
# 确保 Worker 监听正确的队列
celery -A celery_app worker --queues=basic,advanced,realworld
```

**可能原因 2: 任务序列化格式不匹配**
```python
# 检查配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
)
```

**可能原因 3: Redis 连接问题**
```python
# 检查 Redis 连接
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # 应该返回 True
```

**可能原因 4: 任务路由配置错误**
```python
# 检查任务路由
app.conf.task_routes
# 确保任务名称匹配路由规则
```

**可能原因 5: Worker 和 Client 使用不同的 Celery 应用实例**
```python
# 确保 Worker 和 Client 使用相同的应用配置
# Worker: celery -A celery_app worker
# Client: from celery_app import app
```

**排查步骤**:
1. 检查 Worker 日志，查看是否有错误信息
2. 使用 `celery -A celery_app inspect active_queues` 检查队列
3. 使用 `redis-cli` 检查队列中是否有任务
4. 检查任务路由配置
5. 检查序列化格式配置

---

## 答案和评分标准

### 评分标准

| 部分 | 分值 | 说明 |
|------|------|------|
| 选择题 | 20 分 | 每题 2 分，答对得分 |
| 填空题 | 20 分 | 每空 2 分，答对得分 |
| 判断题 | 10 分 | 每题 2 分，答对得分 |
| 简答题 | 20 分 | 每题 5 分，按要点给分 |
| 编程题 | 20 分 | 每题 10 分，按功能实现给分 |
| 场景分析题 | 20 分 | 每题 10 分，按分析深度给分 |
| 故障排查题 | 10 分 | 按排查思路和解决方案给分 |

### 等级评定

- **90-100 分**: 🌟🌟🌟🌟🌟 优秀
  - 深入理解 Celery 的核心机制
  - 能够解决复杂的实际问题
  - 能够优化和调优 Celery 应用

- **80-89 分**: 🌟🌟🌟🌟 良好
  - 理解 Celery 的核心概念
  - 能够处理常见的配置和问题
  - 能够编写基本的 Celery 应用

- **70-79 分**: 🌟🌟🌟 及格
  - 掌握 Celery 的基础知识
  - 能够使用 Celery 的基本功能
  - 需要进一步学习高级特性

- **<70 分**: 🌟🌟 需要重新学习
  - 基础知识不牢固
  - 建议重新学习相关文档
  - 多做实践练习

---

## 学习建议

### 如果得分 < 70 分

1. **重新学习基础文档**:
   - `CELERY_EXECUTION_MODEL.md` - 执行模型
   - `TASK_DISTRIBUTION.md` - 任务分配机制
   - `PREFORK_MECHANISM.md` - Prefork 机制

2. **实践练习**:
   - 运行项目中的示例代码
   - 尝试修改配置，观察效果
   - 使用不同 Pool 模式，对比性能

### 如果得分 70-89 分

1. **深入学习**:
   - `TASK_ROUTES_DEEP_DIVE.md` - 任务路由
   - `CELERY_CONFIG.md` - 配置详解
   - `TROUBLESHOOTING.md` - 故障排查

2. **实践优化**:
   - 优化现有配置
   - 解决实际问题
   - 性能调优

### 如果得分 90+ 分

1. **高级应用**:
   - 分布式部署
   - 监控和告警
   - 性能优化
   - 最佳实践

2. **贡献**:
   - 帮助他人解决问题
   - 分享经验
   - 改进项目

---

## 附加挑战题（不计入总分，供深入学习）

### 挑战题 1: 实现自定义任务路由

请实现一个自定义任务路由函数，根据任务参数动态路由到不同队列。

**要求**:
- 如果任务参数中包含 `priority='high'`，路由到 `critical` 队列
- 如果任务参数中包含 `priority='low'`，路由到 `low` 队列
- 其他情况路由到 `normal` 队列

### 挑战题 2: 实现任务监控和告警

请实现一个任务监控系统，当任务执行时间超过阈值时发送告警。

**要求**:
- 监控所有任务的执行时间
- 如果执行时间超过 60 秒，发送告警
- 使用信号（Signals）实现

### 挑战题 3: 性能优化分析

请分析以下场景，提出优化方案：

**场景**:
- 10000 个 I/O 密集型任务（每个任务执行 1 秒）
- 使用 Prefork 模式，`--concurrency=4`
- 总执行时间: 2500 秒

**问题**: 如何优化到 100 秒以内？

---

**祝考试顺利！** 🚀

