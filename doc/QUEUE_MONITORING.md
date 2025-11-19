# 📊 消息队列监控指南

本指南介绍如何在运行中查看 Celery 消息队列的变化。

## 🛠️ 监控工具

### 1. 实时队列监控器（推荐）

**文件**: `queue_monitor.py`

实时显示队列状态、Worker 状态、任务执行情况等。

#### 使用方法

```bash
# 基本使用（每2秒刷新）
python3 queue_monitor.py

# 自定义刷新间隔（每1秒刷新）
python3 queue_monitor.py --interval 1

# 显示详细信息（包括已注册的任务）
python3 queue_monitor.py --details

# 连接远程 Redis
python3 queue_monitor.py --host 192.168.1.100 --port 6379

# 连接带密码的 Redis
python3 queue_monitor.py --password your_password
```

#### 显示内容

- ✅ **队列信息**: 各队列的长度和任务数量
- ✅ **Worker 状态**: Worker 池大小、成功/失败任务数
- ✅ **正在执行的任务**: 当前正在执行的任务详情
- ✅ **已保留的任务**: Worker 已获取但未执行的任务
- ✅ **计划执行的任务**: 定时任务和延迟任务
- ✅ **已注册的任务**: Worker 支持的所有任务类型（--details）

#### 示例输出

```
================================================================================
⏰ 2024-01-15 14:30:25
================================================================================

📦 队列信息:
--------------------------------------------------------------------------------
  🟢 celery              :    5 个任务
  ⚪ basic               :    0 个任务
  🟢 advanced            :    2 个任务
  总计: 7 个任务在队列中

👷 Worker 状态:
--------------------------------------------------------------------------------
  celery@hostname
    池大小: 4
    成功: 150, 失败: 2

🔄 正在执行的任务:
--------------------------------------------------------------------------------
  celery@hostname: 2 个任务
    - tasks.basic_tasks.add (ID: abc123def456...)
    - tasks.advanced_tasks.fetch_data (ID: xyz789ghi012...)
```

### 2. Redis 队列查看器

**文件**: `redis_queue_viewer.py`

直接查看 Redis 中的原始队列内容，不依赖 Celery。

#### 使用方法

```bash
# 基本使用
python3 redis_queue_viewer.py

# 连接远程 Redis
python3 redis_queue_viewer.py --host 192.168.1.100 --port 6379

# 连接带密码的 Redis
python3 redis_queue_viewer.py --password your_password
```

#### 显示内容

- ✅ **Redis 键列表**: 所有与 Celery 相关的键
- ✅ **队列内容**: 队列中的任务详情（JSON 格式）
- ✅ **任务结果**: 最近的任务执行结果
- ✅ **统计信息**: 队列和结果的统计

#### 示例输出

```
📦 队列: celery (长度: 5)
  ----------------------------------------------------------------------------
  [1] 任务: tasks.basic_tasks.add
      ID: abc123def456...
      参数: [4, 5]
  
  [2] 任务: tasks.advanced_tasks.fetch_data
      ID: xyz789ghi012...
      参数: ['database']
```

## 🔍 其他监控方法

### 方法 1: 使用 Redis CLI

```bash
# 连接 Redis
redis-cli

# 查看队列长度
LLEN celery

# 查看队列内容（不删除）
LRANGE celery 0 -1

# 查看所有键
KEYS *

# 查看任务结果
GET celery-task-meta-{task_id}
```

### 方法 2: 使用 Celery Inspect

```python
from celery_app import app

# 获取活跃的任务
inspect = app.control.inspect()
active = inspect.active()
print(active)

# 获取队列统计
stats = inspect.stats()
print(stats)

# 获取已注册的任务
registered = inspect.registered()
print(registered)
```

### 方法 3: 使用 Flower（Web 监控工具）

```bash
# 安装 Flower
pip install flower

# 启动 Flower
celery -A celery_app flower

# 访问 http://localhost:5555
```

Flower 提供 Web 界面，可以：
- 查看任务状态
- 查看 Worker 状态
- 查看任务历史
- 查看任务详情

### 方法 4: 使用 monitor.py

项目已包含 `monitor.py`，可以查看任务信息和 Worker 状态：

```bash
# 查看 Worker 统计
python3 monitor.py

# 在代码中使用
from monitor import monitor_task, get_worker_stats

# 监控特定任务
monitor_task('task-id-here')

# 获取 Worker 统计
stats = get_worker_stats()
```

## 📊 监控场景

### 场景 1: 实时监控任务执行

```bash
# 启动监控器
python3 queue_monitor.py --interval 1

# 在另一个终端提交任务
python3 examples/basic_usage.py

# 观察队列变化
```

### 场景 2: 查看队列积压

```bash
# 查看队列内容
python3 redis_queue_viewer.py

# 或使用 Redis CLI
redis-cli
> LLEN celery
> LRANGE celery 0 9
```

### 场景 3: 调试任务问题

```bash
# 查看任务结果
python3 redis_queue_viewer.py

# 查看正在执行的任务
python3 queue_monitor.py

# 查看 Worker 日志
celery -A celery_app worker --loglevel=debug
```

### 场景 4: 性能监控

```bash
# 监控队列长度变化
python3 queue_monitor.py --interval 0.5

# 观察：
# - 队列是否积压
# - Worker 是否繁忙
# - 任务执行时间
```

## 🎯 最佳实践

### 1. 开发环境

```bash
# 使用实时监控器，快速刷新
python3 queue_monitor.py --interval 1 --details
```

### 2. 生产环境

```bash
# 使用 Flower 进行 Web 监控
celery -A celery_app flower --port=5555

# 或使用监控脚本定期检查
python3 queue_monitor.py --interval 5
```

### 3. 调试问题

```bash
# 1. 查看队列内容
python3 redis_queue_viewer.py

# 2. 查看 Worker 状态
python3 queue_monitor.py

# 3. 查看任务结果
redis-cli GET celery-task-meta-{task_id}
```

## 🔧 故障排查

### 问题 1: 队列中有任务但 Worker 不执行

**检查**:
```bash
# 1. 检查 Worker 是否运行
python3 queue_monitor.py

# 2. 检查队列名称是否匹配
python3 redis_queue_viewer.py

# 3. 检查 Worker 启动时的队列配置
celery -A celery_app worker --queues=celery,basic,advanced
```

### 问题 2: 任务一直处于 PENDING 状态

**检查**:
```bash
# 1. 查看队列内容
python3 redis_queue_viewer.py

# 2. 查看 Worker 状态
python3 queue_monitor.py

# 3. 检查任务路由配置
# 查看 celery_app.py 中的 task_routes
```

### 问题 3: 队列积压严重

**检查**:
```bash
# 1. 查看队列长度
python3 queue_monitor.py

# 2. 查看 Worker 数量
python3 queue_monitor.py

# 3. 增加 Worker 数量
celery -A celery_app worker --concurrency=8
```

## 📚 相关文件

- `queue_monitor.py`: 实时队列监控器
- `redis_queue_viewer.py`: Redis 队列查看器
- `monitor.py`: 任务和 Worker 监控工具
- `test_redis_connection.py`: Redis 连接测试工具

## 💡 提示

1. **实时监控**: 使用 `queue_monitor.py` 实时查看队列变化
2. **详细查看**: 使用 `redis_queue_viewer.py` 查看原始队列内容
3. **Web 界面**: 使用 Flower 获得更好的可视化体验
4. **定期检查**: 在生产环境中定期检查队列状态

---

**现在你可以轻松监控 Celery 消息队列的变化了！** 🎉

