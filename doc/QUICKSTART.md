# 🚀 Celery 快速开始指南

## 5 分钟快速上手

### 步骤 1: 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install celery redis
```

### 步骤 2: 启动 Redis

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# 或使用 Docker
docker run -d -p 6379:6379 redis:latest

# 验证 Redis 是否运行
redis-cli ping
# 应该返回: PONG
```

### 步骤 3: 启动 Celery Worker

打开一个新的终端窗口：

```bash
cd /Users/umu/Documents/tech/my-github/celery_learning

# 启动 Worker
celery -A celery_app worker --loglevel=info
```

你应该看到类似这样的输出：
```
[tasks]
  . tasks.basic_tasks.add
  . tasks.basic_tasks.multiply
  ...

[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] celery@hostname ready.
```

### 步骤 4: 运行你的第一个任务

在另一个终端窗口：

```bash
cd /Users/umu/Documents/tech/my-github/celery_learning

# 运行交互式菜单
python main.py

# 或直接运行示例
python examples/basic_usage.py
```

### 步骤 5: 查看结果

在 Worker 终端，你应该看到任务执行日志：
```
[INFO/MainProcess] Task tasks.basic_tasks.add[xxx] received
[INFO/ForkPoolWorker-1] 计算 4 + 5
[INFO/ForkPoolWorker-1] 结果: 9
[INFO/MainProcess] Task tasks.basic_tasks.add[xxx] succeeded in 0.01s: 9
```

## 📝 最简单的示例

创建一个新文件 `test_celery.py`:

```python
from celery_app import app
from tasks.basic_tasks import add

# 提交任务
result = add.delay(4, 5)

# 获取结果
print(f"任务ID: {result.id}")
print(f"结果: {result.get()}")
```

运行：
```bash
python test_celery.py
```

## 🎯 理解关键概念

### 1. 任务定义

```python
from celery_app import app

@app.task
def my_task(x, y):
    return x + y
```

### 2. 异步调用

```python
# 异步调用（不阻塞）
result = my_task.delay(4, 5)

# 同步等待结果
value = result.get()
```

### 3. 任务状态

```python
result = my_task.delay(4, 5)

print(result.state)  # PENDING, SUCCESS, FAILURE 等
print(result.ready())  # True/False
print(result.get())  # 获取结果
```

## 🔧 常见问题

### Q: Worker 无法连接 Redis

**A**: 检查 Redis 是否运行：
```bash
redis-cli ping
```

### Q: 任务一直处于 PENDING 状态

**A**: 确保 Worker 正在运行：
```bash
celery -A celery_app worker --loglevel=info
```

### Q: 如何查看任务结果？

**A**: 使用任务 ID：
```python
from celery.result import AsyncResult
from celery_app import app

result = AsyncResult('task-id-here', app=app)
print(result.get())
```

## 📚 下一步

1. 阅读 `README.md` 了解完整功能
2. 查看 `DISTRIBUTED_MESSAGING.md` 深入理解原理
3. 运行 `examples/` 目录下的所有示例
4. 尝试修改任务，创建自己的任务

## 💡 提示

- **Worker 和 Client 可以在不同的机器上运行**（分布式）
- **可以启动多个 Worker** 提高处理能力
- **使用 `result.get(timeout=10)` 设置超时**
- **任务可以返回任何可序列化的对象**

---

**现在你已经掌握了 Celery 的基础！开始探索更多功能吧！** 🎉

