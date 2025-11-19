# Celery 深入学习项目

这是一个完整的 Celery 学习项目，通过实际例子帮助你深入理解 Celery 的实现原理和分布式消息系统，并掌握 Celery 在实际工程中的使用。

## 📚 项目结构

```
celery_learning/
├── celery_app.py              # Celery 应用配置
├── tasks/                      # 任务模块
│   ├── __init__.py
│   ├── basic_tasks.py         # 基础任务示例
│   ├── advanced_tasks.py       # 高级任务示例
│   └── realworld_tasks.py      # 实际工程任务示例
├── examples/                   # 使用示例
│   ├── basic_usage.py         # 基础用法示例
│   ├── advanced_usage.py      # 高级用法示例
│   └── realworld_usage.py      # 实际工程用法示例
├── monitor.py                  # 监控工具
├── start_worker.sh            # Worker 启动脚本
├── start_beat.sh              # Beat 启动脚本
└── README.md                   # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install celery redis
```

### 2. 启动 Redis

Celery 使用 Redis 作为消息代理和结果后端，需要先启动 Redis：

**方式 1: 使用 Docker Compose（推荐）**
```bash
docker-compose up -d
```

**方式 2: 使用 Docker 命令**
```bash
docker run -d -p 6379:6379 --name celery_redis redis:7-alpine
```

**方式 3: 本地安装**
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

**验证 Redis 运行**:
```bash
# Docker
docker exec -it celery_redis redis-cli ping
# 或
redis-cli ping
# 应该返回: PONG
```

> 💡 **提示**: 详细 Docker Redis 连接说明请查看 [DOCKER_REDIS.md](DOCKER_REDIS.md)

### 3. 启动 Celery Worker

```bash
# 方式1: 使用脚本
./start_worker.sh

# 方式2: 直接命令
celery -A celery_app worker --loglevel=info --queues=basic,advanced,realworld
```

### 4. 启动 Celery Beat（定时任务调度器）

如果需要运行定时任务，需要启动 Beat：

```bash
# 方式1: 使用脚本
./start_beat.sh

# 方式2: 直接命令
celery -A celery_app beat --loglevel=info
```

### 5. 运行示例

```bash
# 基础用法示例
python examples/basic_usage.py

# 高级用法示例
python examples/advanced_usage.py

# 实际工程用法示例
python examples/realworld_usage.py
```

## 📖 学习内容

### 1. Celery 核心概念

#### 消息代理（Message Broker）
- **作用**: 负责接收和分发任务消息
- **常用选择**: Redis、RabbitMQ、Amazon SQS
- **本项目使用**: Redis

#### 结果后端（Result Backend）
- **作用**: 存储任务执行结果
- **常用选择**: Redis、Memcached、数据库
- **本项目使用**: Redis

#### Worker
- **作用**: 执行任务的进程
- **特点**: 可以水平扩展，支持多进程/多线程

#### 任务（Task）
- **定义**: 使用 `@app.task` 装饰器定义的函数
- **执行**: 异步执行，不阻塞主程序

### 2. 基础任务示例

查看 `tasks/basic_tasks.py` 了解：
- ✅ 简单任务定义和调用
- ✅ 带参数的任务
- ✅ 任务状态跟踪
- ✅ 进度更新
- ✅ 定时任务

**示例代码**:
```python
from tasks.basic_tasks import add, multiply

# 异步调用任务
result = add.delay(4, 5)
print(result.get())  # 获取结果
```

### 3. 高级任务示例

查看 `tasks/advanced_tasks.py` 了解：
- ✅ **任务链（Chain）**: 顺序执行多个任务
- ✅ **任务组（Group）**: 并行执行多个任务
- ✅ **Chord**: 并行执行后聚合结果
- ✅ **任务重试**: 自动重试机制
- ✅ **自定义重试策略**: 指数退避、固定延迟等

**示例代码**:
```python
from celery import chain, group, chord

# 任务链：顺序执行
workflow = chain(
    fetch_data.s('source'),
    process_item.s(),
    save_result.s()
)

# 任务组：并行执行
job = group(
    fetch_data.s('source1'),
    fetch_data.s('source2'),
)

# Chord：并行执行后回调
chord_task = chord(header)(callback)
```

### 4. 实际工程任务示例

查看 `tasks/realworld_tasks.py` 了解：
- ✅ 邮件发送任务（带重试）
- ✅ 图片处理任务（带进度）
- ✅ 数据导入/导出任务
- ✅ 报告生成任务
- ✅ 文件清理任务

**示例代码**:
```python
from tasks.realworld_tasks import send_email, process_image

# 发送邮件
result = send_email.delay(
    to_email='user@example.com',
    subject='欢迎',
    body='内容'
)

# 处理图片
result = process_image.delay(
    image_path='photo.jpg',
    operations=['resize', 'crop', 'filter']
)
```

## 🔧 Celery 配置详解

查看 `celery_app.py` 了解完整配置：

### 消息代理和结果后端
```python
app = Celery(
    'celery_learning',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)
```

### 任务路由
```python
task_routes={
    'tasks.basic_tasks.*': {'queue': 'basic'},
    'tasks.advanced_tasks.*': {'queue': 'advanced'},
    'tasks.realworld_tasks.*': {'queue': 'realworld'},
}
```

### 定时任务配置
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
}
```

## 📊 监控和管理

### 使用监控工具

```python
from monitor import monitor_task, get_worker_stats

# 监控任务执行
monitor_task('task-id-here')

# 获取 Worker 统计
stats = get_worker_stats()
```

### 使用 Flower（可选）

Flower 是 Celery 的 Web 监控工具：

```bash
pip install flower
celery -A celery_app flower
```

然后访问 http://localhost:5555 查看监控界面。

## 🎯 实际工程最佳实践

### 1. 错误处理和重试

```python
@app.task(bind=True, max_retries=3)
def my_task(self, data):
    try:
        # 任务逻辑
        pass
    except Exception as exc:
        # 指数退避重试
        raise self.retry(countdown=2 ** self.request.retries, exc=exc)
```

### 2. 任务优先级

```python
# 高优先级任务
high_priority_task.apply_async(args=[...], priority=9)

# 低优先级任务
low_priority_task.apply_async(args=[...], priority=1)
```

### 3. 任务超时设置

```python
app.conf.update(
    task_time_limit=300,      # 硬超时：5分钟
    task_soft_time_limit=240,  # 软超时：4分钟
)
```

### 4. Worker 配置优化

```python
app.conf.update(
    worker_prefetch_multiplier=4,      # 每个 worker 预取任务数
    worker_max_tasks_per_child=1000,   # 防止内存泄漏
)
```

### 5. 结果过期时间

```python
app.conf.update(
    result_expires=3600,  # 结果1小时后过期
)
```

## 🔍 深入理解分布式消息系统

### Celery 工作流程

1. **任务提交**: 应用调用 `task.delay()` 或 `task.apply_async()`
2. **消息发送**: Celery 将任务消息发送到消息代理（Redis）
3. **消息接收**: Worker 从消息代理获取任务消息
4. **任务执行**: Worker 执行任务
5. **结果存储**: 任务结果存储到结果后端（Redis）
6. **结果获取**: 应用通过 `result.get()` 获取结果

### 消息序列化

- **JSON**: 轻量级，跨语言，但功能有限
- **Pickle**: Python 专用，功能强大，但不安全
- **YAML**: 人类可读，但性能较低

本项目使用 JSON 序列化。

### 任务状态

- **PENDING**: 任务等待执行
- **STARTED**: 任务已开始执行
- **SUCCESS**: 任务成功完成
- **FAILURE**: 任务执行失败
- **RETRY**: 任务正在重试
- **REVOKED**: 任务被撤销

## 🛠️ 常见问题

### 1. Redis 连接失败

确保 Redis 服务正在运行：
```bash
redis-cli ping
# 应该返回 PONG
```

### 2. 任务一直处于 PENDING 状态

- 检查 Worker 是否正在运行
- 检查任务路由配置是否正确
- 检查队列名称是否匹配

### 3. 任务执行超时

调整超时设置：
```python
app.conf.update(
    task_time_limit=600,  # 增加超时时间
)
```

### 4. 内存泄漏

设置 `worker_max_tasks_per_child`：
```python
app.conf.update(
    worker_max_tasks_per_child=1000,
)
```

## 📚 扩展学习

### 推荐阅读

1. [Celery 官方文档](https://docs.celeryq.dev/)
2. [Redis 文档](https://redis.io/docs/)
3. [分布式系统设计](https://en.wikipedia.org/wiki/Distributed_computing)

### 进阶主题

- 任务优先级和路由
- 任务结果后端选择
- 多 Worker 部署
- 任务监控和告警
- 性能优化和调优

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**祝你学习愉快！** 🎉

