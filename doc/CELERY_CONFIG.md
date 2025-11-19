# 🔧 Celery 配置详解 - app.conf.update

本文档深入解释 `app.conf.update()` 中每个配置项的含义、作用和使用场景。

## 📋 配置分类

Celery 配置可以分为以下几大类：
1. **任务序列化配置**
2. **时区配置**
3. **任务路由配置**
4. **任务优先级配置**
5. **超时配置**
6. **Worker 配置**
7. **结果后端配置**
8. **定时任务配置**

---

## 1. 任务序列化配置

### 配置项

```python
task_serializer='json',        # 任务序列化格式
accept_content=['json'],       # 接受的内容类型
result_serializer='json',      # 结果序列化格式
```

### 详细说明

#### `task_serializer`
- **作用**: 指定任务参数如何序列化（转换为字符串）以便在消息队列中传输
- **可选值**:
  - `'json'`: JSON 格式（推荐，跨语言兼容）
  - `'pickle'`: Python pickle 格式（仅 Python，不安全）
  - `'yaml'`: YAML 格式（人类可读，但性能较低）
  - `'msgpack'`: MessagePack 格式（二进制，高效）
- **为什么重要**: 任务参数需要序列化才能在进程间传输

#### `accept_content`
- **作用**: 指定 Worker 接受哪些序列化格式的任务
- **安全考虑**: 只接受 `['json']` 可以防止代码注入攻击（pickle 不安全）
- **示例**: `['json', 'pickle']` 表示接受两种格式

#### `result_serializer`
- **作用**: 指定任务结果如何序列化存储到结果后端
- **应与 `task_serializer` 一致**: 保持一致性，避免序列化/反序列化问题

### 实际影响

```python
# 使用 JSON（安全，跨语言）
task_serializer='json'  # ✅ 推荐

# 使用 Pickle（不安全，仅 Python）
task_serializer='pickle'  # ⚠️ 不推荐，有安全风险
```

---

## 2. 时区配置

### 配置项

```python
timezone='Asia/Shanghai',  # 时区设置
enable_utc=True,           # 启用 UTC
```

### 详细说明

#### `timezone`
- **作用**: 设置 Celery 使用的时区
- **影响范围**: 
  - 定时任务（Beat）的执行时间
  - 任务日志中的时间戳
  - 任务结果中的时间字段
- **常见值**:
  - `'Asia/Shanghai'`: 中国时区（UTC+8）
  - `'UTC'`: 协调世界时
  - `'America/New_York'`: 美国东部时区
- **为什么重要**: 确保定时任务在正确的时间执行

#### `enable_utc`
- **作用**: 是否启用 UTC 时间
- **推荐**: `True`（内部使用 UTC，显示时转换为本地时区）
- **好处**: 避免夏令时和时区转换问题

### 实际影响

```python
# 定时任务会在北京时间凌晨2点执行
schedule=crontab(hour=2, minute=0)  # 基于 timezone='Asia/Shanghai'
```

---

## 3. 任务路由配置

### 配置项

```python
task_routes={
    'tasks.basic_tasks.*': {'queue': 'basic'},
    'tasks.advanced_tasks.*': {'queue': 'advanced'},
    'tasks.realworld_tasks.*': {'queue': 'realworld'},
}
```

### 详细说明

#### `task_routes`
- **作用**: 将不同类型的任务路由到不同的队列
- **格式**: 字典，键是任务名称模式，值是路由配置
- **模式匹配**:
  - `'tasks.basic_tasks.*'`: 匹配所有 `tasks.basic_tasks` 模块下的任务
  - `'tasks.basic_tasks.add'`: 匹配特定任务
  - `'*.email.*'`: 匹配所有包含 `email` 的任务

#### 路由配置选项

```python
task_routes={
    'tasks.high_priority.*': {
        'queue': 'high_priority',      # 队列名称
        'exchange': 'tasks',           # 交换机名称
        'routing_key': 'high',         # 路由键
        'priority': 9,                 # 优先级
    },
}
```

### 实际应用场景

1. **任务隔离**: 不同类型的任务使用不同队列，互不影响
2. **优先级处理**: 高优先级任务使用专用队列和 Worker
3. **资源分配**: CPU 密集型任务和 I/O 密集型任务分离

### Worker 启动示例

```bash
# 只处理基础任务
celery -A celery_app worker --queues=basic

# 处理多个队列
celery -A celery_app worker --queues=basic,advanced

# 处理所有队列
celery -A celery_app worker --queues=basic,advanced,realworld
```

---

## 4. 任务优先级配置

### 配置项

```python
task_default_priority=5,  # 默认优先级
```

### 详细说明

#### `task_default_priority`
- **作用**: 设置任务的默认优先级
- **范围**: 0-9（数字越大优先级越高）
- **使用场景**: 当任务没有明确指定优先级时使用

#### 任务级别优先级

```python
# 在任务调用时指定优先级
task.apply_async(args=[...], priority=9)  # 高优先级
task.apply_async(args=[...], priority=1)  # 低优先级
```

### 优先级队列

```python
# 需要启用优先级队列
task_default_queue='default'
task_default_exchange='tasks'
task_default_routing_key='default'
task_default_exchange_type='direct'
```

---

## 5. 超时配置

### 配置项

```python
task_time_limit=300,      # 硬超时：5分钟
task_soft_time_limit=240, # 软超时：4分钟
```

### 详细说明

#### `task_time_limit`（硬超时）
- **作用**: 任务的最大执行时间（秒）
- **超时行为**: Worker 进程会被强制终止
- **影响**: 可能导致数据不一致，应谨慎设置
- **推荐**: 设置为任务正常执行时间的 2-3 倍

#### `task_soft_time_limit`（软超时）
- **作用**: 任务的软超时时间（秒）
- **超时行为**: 触发 `SoftTimeLimitExceeded` 异常，任务可以捕获并优雅退出
- **好处**: 允许任务清理资源、保存状态
- **推荐**: 设置为硬超时的 80%

### 任务中处理超时

```python
from celery.exceptions import SoftTimeLimitExceeded

@app.task(bind=True, soft_time_limit=240, time_limit=300)
def my_task(self):
    try:
        # 任务逻辑
        pass
    except SoftTimeLimitExceeded:
        # 优雅处理超时
        self.update_state(state='FAILURE', meta={'error': '任务超时'})
        # 清理资源
        cleanup()
```

### 实际应用

```python
# 快速任务
task_time_limit=60        # 1分钟
task_soft_time_limit=50   # 50秒

# 长时间任务
task_time_limit=3600      # 1小时
task_soft_time_limit=3000 # 50分钟
```

---

## 6. Worker 配置

### 配置项

```python
worker_prefetch_multiplier=4,      # 每个 worker 预取的任务数
worker_max_tasks_per_child=1000,    # 每个 worker 子进程执行的最大任务数
```

### 详细说明

#### `worker_prefetch_multiplier`
- **作用**: 每个 Worker 子进程预取的任务数量
- **计算公式**: 预取数 = `worker_prefetch_multiplier` × Worker 并发数
- **影响**:
  - **值大**: 提高吞吐量，但可能导致任务分配不均
  - **值小**: 任务分配更均匀，但可能降低吞吐量
- **推荐值**: 2-4

#### `worker_max_tasks_per_child`
- **作用**: 每个 Worker 子进程执行的最大任务数，达到后重启子进程
- **目的**: 防止内存泄漏
- **机制**: 执行指定数量任务后，Worker 会创建新的子进程
- **推荐值**: 1000-5000（根据任务内存使用情况调整）

### 其他 Worker 配置

```python
app.conf.update(
    # 并发数（进程数）
    worker_concurrency=4,           # 默认是 CPU 核心数
    
    # Worker 池类型
    worker_pool='prefork',          # prefork, solo, eventlet, gevent
    
    # 任务确认
    task_acks_late=True,            # 任务完成后才确认
    task_reject_on_worker_lost=True,  # Worker 丢失时拒绝任务
    
    # 任务预取
    worker_disable_rate_limits=False, # 禁用速率限制
)
```

### 实际应用

```python
# CPU 密集型任务
worker_concurrency=4              # 等于 CPU 核心数
worker_prefetch_multiplier=2       # 较小的预取数

# I/O 密集型任务
worker_pool='gevent'              # 使用协程
worker_concurrency=100             # 更多并发
worker_prefetch_multiplier=10      # 更大的预取数
```

---

## 7. 结果后端配置

### 配置项

```python
result_expires=3600,  # 结果过期时间（秒）
```

### 详细说明

#### `result_expires`
- **作用**: 任务结果在结果后端中的过期时间（秒）
- **目的**: 防止结果数据无限增长，节省存储空间
- **默认**: 1 天（86400 秒）
- **推荐**: 根据实际需求设置（1小时到几天不等）

### 其他结果后端配置

```python
app.conf.update(
    # 结果过期时间
    result_expires=3600,           # 1小时后过期
    
    # 结果序列化
    result_serializer='json',      # 与 task_serializer 一致
    
    # 结果压缩
    result_compression='gzip',     # 压缩结果（可选）
    
    # 结果持久化
    result_persistent=True,        # 持久化结果（RabbitMQ）
)
```

### 实际应用

```python
# 临时结果（不需要长期保存）
result_expires=300  # 5分钟后过期

# 重要结果（需要保存较长时间）
result_expires=86400  # 24小时后过期

# 永久保存（不推荐，会占用大量空间）
result_expires=None  # 不过期
```

---

## 8. 定时任务配置（Beat Schedule）

### 配置项

```python
beat_schedule={
    'periodic-simple-task': {
        'task': 'tasks.basic_tasks.periodic_task',
        'schedule': 30.0,  # 每30秒
    },
    'daily-task': {
        'task': 'tasks.basic_tasks.daily_task',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
    'weekly-task': {
        'task': 'tasks.basic_tasks.weekly_task',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # 每周一上午9点
    },
}
```

### 详细说明

#### `beat_schedule`
- **作用**: 定义定时任务的调度计划
- **格式**: 字典，键是任务名称，值是调度配置
- **需要启动**: Celery Beat 进程来执行定时任务

#### 调度方式

**1. 固定间隔（秒）**
```python
'schedule': 30.0  # 每30秒执行一次
```

**2. Crontab 表达式**
```python
from celery.schedules import crontab

# 每天凌晨2点
crontab(hour=2, minute=0)

# 每周一上午9点
crontab(hour=9, minute=0, day_of_week=1)

# 每月1号凌晨0点
crontab(day_of_month=1, hour=0, minute=0)

# 每5分钟
crontab(minute='*/5')
```

**3. Solar 调度（基于日出日落）**
```python
from celery.schedules import solar

# 每天日出时执行
solar('sunrise', 40.7128, -74.0060)  # 纽约坐标
```

**4. 自定义调度**
```python
from celery.schedules import schedule

# 自定义间隔
schedule(run_every=timedelta(minutes=5))
```

### 定时任务配置选项

```python
beat_schedule={
    'my-task': {
        'task': 'tasks.my_task',
        'schedule': 30.0,
        'args': (16, 16),           # 位置参数
        'kwargs': {'key': 'value'}, # 关键字参数
        'options': {
            'queue': 'high_priority',  # 队列
            'priority': 9,              # 优先级
            'expires': 3600,            # 任务过期时间
        },
    },
}
```

### 启动 Beat

```bash
# 启动定时任务调度器
celery -A celery_app beat --loglevel=info

# 或使用脚本
./start_beat.sh
```

---

## 🔍 完整配置示例

### 生产环境配置

```python
app.conf.update(
    # 序列化（安全）
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务路由
    task_routes={
        'tasks.critical.*': {'queue': 'critical', 'priority': 9},
        'tasks.normal.*': {'queue': 'normal', 'priority': 5},
        'tasks.low.*': {'queue': 'low', 'priority': 1},
    },
    
    # 超时
    task_time_limit=600,      # 10分钟硬超时
    task_soft_time_limit=540, # 9分钟软超时
    
    # Worker
    worker_prefetch_multiplier=2,
    worker_max_tasks_per_child=1000,
    worker_concurrency=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 结果
    result_expires=7200,  # 2小时后过期
    
    # 定时任务
    beat_schedule={
        'daily-backup': {
            'task': 'tasks.backup.daily_backup',
            'schedule': crontab(hour=2, minute=0),
        },
    },
)
```

### 开发环境配置

```python
app.conf.update(
    # 开发环境使用更宽松的配置
    task_serializer='json',
    task_time_limit=3600,  # 更长的超时时间
    worker_prefetch_multiplier=4,
    result_expires=86400,  # 结果保存更久，方便调试
)
```

---

## 📊 配置优先级

配置的优先级（从高到低）：
1. **任务级别配置**（`@app.task` 装饰器参数）
2. **调用时配置**（`apply_async()` 参数）
3. **应用配置**（`app.conf.update()`）
4. **默认配置**

---

## 🎯 最佳实践

1. **序列化**: 始终使用 `json`，避免 `pickle` 的安全风险
2. **超时**: 设置合理的超时时间，并处理 `SoftTimeLimitExceeded`
3. **Worker**: 根据任务类型调整并发数和预取数
4. **结果**: 设置合理的过期时间，避免占用过多存储
5. **路由**: 使用任务路由实现任务隔离和优先级
6. **时区**: 明确设置时区，避免定时任务执行时间错误

---

## 📚 参考资源

- [Celery 配置文档](https://docs.celeryq.dev/en/stable/userguide/configuration.html)
- [任务路由文档](https://docs.celeryq.dev/en/stable/userguide/routing.html)
- [定时任务文档](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)

---

**通过理解这些配置，你可以根据实际需求优化 Celery 的性能和可靠性！** 🚀

