# 🔧 Celery 故障排查指南

## 常见错误和解决方案

### 错误 1: `TypeError: function() takes 0 positional arguments but N were given`

**错误信息**:
```
TypeError: hello_world() takes 0 positional arguments but 2 were given
```

**原因**:
- Worker 中加载的任务定义与当前代码不一致
- Worker 需要重启以加载新的任务定义
- Worker 可能在使用旧版本的任务代码

**解决方案**:

1. **重启 Worker**:
   ```bash
   # 停止当前 Worker (Ctrl+C)
   # 重新启动 Worker
   celery -A celery_app worker --loglevel=info
   ```

2. **确保 Worker 加载了正确的代码**:
   - 检查 Worker 启动时的工作目录
   - 确保 Worker 可以导入任务模块
   - 检查 Python 路径是否正确

3. **清除旧的任务结果**（可选）:
   ```bash
   # 使用 Redis CLI
   redis-cli FLUSHDB
   ```

4. **验证任务定义**:
   ```python
   from tasks.basic_tasks import hello_world
   import inspect
   print(inspect.signature(hello_world))
   # 应该显示: (x, y)
   ```

### 错误 2: 任务一直处于 PENDING 状态

**原因**:
- Worker 未运行
- Worker 未监听相应的队列
- 任务路由配置错误

**解决方案**:

1. **检查 Worker 是否运行**:
   ```bash
   # 使用监控工具
   python3 queue_monitor.py
   
   # 或使用 Celery inspect
   celery -A celery_app inspect active
   ```

2. **检查 Worker 监听的队列**:
   ```bash
   # 启动 Worker 时指定队列
   celery -A celery_app worker --queues=basic,advanced,realworld
   ```

3. **检查任务路由**:
   ```python
   from celery_app import app
   print(app.conf.task_routes)
   ```

### 错误 3: `ConnectionError: Error connecting to Redis`

**原因**:
- Redis 未运行
- Redis 连接配置错误
- 网络问题

**解决方案**:

1. **检查 Redis 是否运行**:
   ```bash
   # 测试 Redis 连接
   redis-cli ping
   # 应该返回: PONG
   ```

2. **使用 Docker Redis**:
   ```bash
   docker-compose up -d
   # 或
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **检查连接配置**:
   ```python
   # 查看 celery_app.py 中的 Redis 配置
   # 或使用环境变量
   export REDIS_HOST=localhost
   export REDIS_PORT=6379
   ```

4. **测试连接**:
   ```bash
   python3 test_redis_connection.py
   ```

### 错误 4: `ImportError: No module named 'tasks'`

**原因**:
- Python 路径配置错误
- 任务模块未正确导入

**解决方案**:

1. **检查导入路径**:
   ```python
   # 确保在项目根目录运行
   import sys
   from pathlib import Path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

2. **检查 Worker 启动目录**:
   ```bash
   # 在项目根目录启动 Worker
   cd /path/to/celery_learning
   celery -A celery_app worker
   ```

3. **检查任务模块**:
   ```python
   # 确保 tasks/__init__.py 存在
   # 确保任务模块可以被导入
   python3 -c "from tasks.basic_tasks import add; print('OK')"
   ```

### 错误 5: 任务执行超时

**原因**:
- 任务执行时间超过超时设置
- 任务陷入死循环
- 资源不足

**解决方案**:

1. **增加超时时间**:
   ```python
   # 在 celery_app.py 中
   app.conf.update(
       task_time_limit=600,      # 增加硬超时
       task_soft_time_limit=540, # 增加软超时
   )
   ```

2. **在任务中处理超时**:
   ```python
   from celery.exceptions import SoftTimeLimitExceeded
   
   @app.task(bind=True, soft_time_limit=240)
   def my_task(self):
       try:
           # 任务逻辑
           pass
       except SoftTimeLimitExceeded:
           # 优雅处理超时
           cleanup()
           raise
   ```

3. **检查任务逻辑**:
   - 确保任务不会陷入死循环
   - 检查是否有阻塞操作
   - 优化任务性能

### 错误 6: Worker 无法连接 Redis

**原因**:
- Redis 配置错误
- 防火墙阻止连接
- Redis 密码错误

**解决方案**:

1. **检查 Redis 配置**:
   ```python
   # 查看 celery_app.py 中的 Redis URL
   print(app.conf.broker_url)
   ```

2. **测试 Redis 连接**:
   ```bash
   python3 test_redis_connection.py
   ```

3. **检查网络和防火墙**:
   ```bash
   # 测试端口是否开放
   telnet localhost 6379
   # 或
   nc -zv localhost 6379
   ```

### 错误 7: 任务结果丢失

**原因**:
- 结果过期时间设置过短
- 结果后端配置错误
- Redis 数据被清除

**解决方案**:

1. **增加结果过期时间**:
   ```python
   app.conf.update(
       result_expires=7200,  # 2小时
   )
   ```

2. **检查结果后端配置**:
   ```python
   print(app.conf.result_backend)
   ```

3. **立即获取结果**:
   ```python
   result = task.delay(args)
   value = result.get(timeout=10)  # 立即获取，不依赖结果后端
   ```

## 🔍 调试技巧

### 1. 启用详细日志

```bash
# Worker 启动时启用 debug 日志
celery -A celery_app worker --loglevel=debug
```

### 2. 使用监控工具

```bash
# 实时监控队列
python3 queue_monitor.py

# 查看队列内容
python3 redis_queue_viewer.py

# 查看 Worker 状态
python3 monitor.py
```

### 3. 检查任务定义

```python
from tasks.basic_tasks import hello_world
import inspect

# 查看函数签名
print(inspect.signature(hello_world))

# 查看任务名称
print(hello_world.name)
```

### 4. 测试任务本地执行

```python
# 不通过 Celery，直接调用函数
from tasks.basic_tasks import hello_world
result = hello_world(1, 2)  # 直接调用，不是 .delay()
print(result)
```

### 5. 使用 Celery Inspect

```python
from celery_app import app

# 检查活跃的 Workers
inspect = app.control.inspect()
active = inspect.active()
print(active)

# 检查已注册的任务
registered = inspect.registered()
print(registered)

# 检查 Worker 统计
stats = inspect.stats()
print(stats)
```

## 📋 检查清单

遇到问题时，按以下顺序检查：

1. ✅ **Redis 是否运行？**
   ```bash
   redis-cli ping
   ```

2. ✅ **Worker 是否运行？**
   ```bash
   python3 queue_monitor.py
   ```

3. ✅ **Worker 是否监听正确的队列？**
   ```bash
   celery -A celery_app worker --queues=basic,advanced,realworld
   ```

4. ✅ **任务定义是否正确？**
   ```python
   from tasks.basic_tasks import hello_world
   import inspect
   print(inspect.signature(hello_world))
   ```

5. ✅ **任务路由配置是否正确？**
   ```python
   from celery_app import app
   print(app.conf.task_routes)
   ```

6. ✅ **Python 路径是否正确？**
   ```python
   import sys
   print(sys.path)
   ```

7. ✅ **是否需要重启 Worker？**
   - 修改任务定义后必须重启 Worker
   - 修改配置后建议重启 Worker

## 🚀 快速修复命令

```bash
# 1. 停止所有 Worker
pkill -f "celery.*worker"

# 2. 清除 Redis 数据（谨慎使用）
redis-cli FLUSHDB

# 3. 重启 Worker
celery -A celery_app worker --loglevel=info

# 4. 测试连接
python3 test_redis_connection.py

# 5. 运行示例
python3 examples/basic_usage.py
```

## 💡 最佳实践

1. **开发时**:
   - 使用 `--loglevel=debug` 查看详细日志
   - 使用监控工具实时查看状态
   - 修改代码后及时重启 Worker

2. **生产环境**:
   - 使用 `--loglevel=info` 或 `warning`
   - 配置合理的超时时间
   - 设置结果过期时间
   - 使用监控和告警

3. **调试技巧**:
   - 先本地测试函数（不通过 Celery）
   - 使用 `print()` 或日志记录调试信息
   - 检查 Worker 日志输出
   - 使用 `queue_monitor.py` 查看队列状态

---

**遇到问题时，按照这个指南逐步排查，大多数问题都能快速解决！** 🎯

