# 🔧 Celery Inspect 错误排查指南

## ❌ 错误信息

```
celery -A ushow_nlp inspect conf

run: local

Error: No nodes replied within time constraint
```

---

## 🎯 问题分析

这个错误表示 Celery 无法与任何 Worker 节点通信。可能的原因：

1. **Worker 未运行**
2. **Worker 无法连接到 Broker**
3. **Worker 和 Client 使用不同的应用配置**
4. **网络连接问题**
5. **Broker 连接配置问题**

---

## 🔍 排查步骤

### 步骤 1: 检查 Worker 是否运行

```bash
# 检查进程
ps aux | grep celery

# 或使用 pgrep
pgrep -f "celery.*worker"

# 检查是否有 Worker 进程
# 应该看到类似这样的进程:
# python -m celery -A ushow_nlp worker ...
```

**如果没有 Worker 进程**:
```bash
# 启动 Worker
celery -A ushow_nlp worker --loglevel=info
```

---

### 步骤 2: 检查 Broker 连接

```bash
# 测试 Redis 连接
redis-cli ping
# 应该返回: PONG

# 如果 Redis 不在本地，检查连接配置
# 查看应用配置中的 broker_url
```

**检查应用配置**:
```python
# 在 Python 中检查
python3 -c "from ushow_nlp import app; print(app.conf.broker_url)"
```

---

### 步骤 3: 检查 Worker 和 Client 使用相同的应用

**问题**: Worker 和 Client 必须使用相同的 Celery 应用实例。

**检查方法**:

```bash
# 1. 检查 Worker 启动命令
ps aux | grep celery
# 应该看到: celery -A ushow_nlp worker ...

# 2. 检查 Client 使用的应用
# 确保 inspect 命令使用的应用名称与 Worker 一致
celery -A ushow_nlp inspect conf
# 这里的 ushow_nlp 必须与 Worker 启动时的应用名称一致
```

**常见错误**:
```bash
# ❌ 错误: Worker 和 Client 使用不同的应用名称
# Worker 启动: celery -A ushow_nlp worker
# Client 使用: celery -A celery_app inspect conf

# ✅ 正确: 使用相同的应用名称
# Worker 启动: celery -A ushow_nlp worker
# Client 使用: celery -A ushow_nlp inspect conf
```

---

### 步骤 4: 检查 Broker 连接配置

**检查应用配置中的 Broker URL**:

```python
# 方法 1: 在 Python 中检查
python3 << EOF
from ushow_nlp import app
print("Broker URL:", app.conf.broker_url)
print("Backend URL:", app.conf.result_backend)
EOF
```

**检查环境变量**:
```bash
# 检查是否有相关的环境变量
env | grep -i redis
env | grep -i broker
env | grep -i celery
```

---

### 步骤 5: 检查网络连接

**在 Kubernetes 环境中**:

```bash
# 1. 检查 Redis 服务是否可达
# 如果 Redis 在另一个 Pod 或服务中
ping <redis-host>
telnet <redis-host> <redis-port>

# 2. 检查 DNS 解析
nslookup <redis-host>

# 3. 检查端口是否开放
nc -zv <redis-host> <redis-port>
```

---

### 步骤 6: 检查 Worker 日志

```bash
# 查看 Worker 日志，查找连接错误
# 如果 Worker 在后台运行，查看日志文件
tail -f /path/to/celery.log

# 或查看系统日志
journalctl -u celery-worker -f

# 在 Kubernetes 中
kubectl logs <pod-name> -f
```

**常见日志错误**:
```
[ERROR] Error connecting to Redis: Connection refused
[ERROR] Error connecting to Broker: Timeout
[ERROR] No connection to broker
```

---

## 🛠️ 解决方案

### 方案 1: 确保 Worker 正在运行

```bash
# 启动 Worker
celery -A ushow_nlp worker \
    --loglevel=info \
    --queues=<your-queues> \
    --concurrency=4

# 在后台运行
nohup celery -A ushow_nlp worker --loglevel=info > celery.log 2>&1 &

# 或使用 systemd/supervisor 管理
```

---

### 方案 2: 检查并修复 Broker 连接

**检查 Redis 连接**:
```python
# 测试脚本
import redis
import os

# 从环境变量或配置获取 Redis 连接信息
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

try:
    if REDIS_PASSWORD:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    else:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    
    r.ping()
    print("✅ Redis 连接成功")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
```

**修复连接配置**:
```python
# 在 ushow_nlp 应用中
import os
from celery import Celery

# 从环境变量读取 Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# 构建 Redis URL
if REDIS_PASSWORD:
    redis_url = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'
else:
    redis_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

app = Celery(
    'ushow_nlp',
    broker=redis_url,
    backend=redis_url,
)
```

---

### 方案 3: 确保应用名称一致

**检查应用名称**:

```python
# 在 ushow_nlp 模块中
# 确保应用名称是 'ushow_nlp'
app = Celery('ushow_nlp', ...)  # ✅ 正确

# 不是
app = Celery('celery_app', ...)  # ❌ 错误
```

**使用正确的应用名称**:
```bash
# Worker 启动
celery -A ushow_nlp worker

# Inspect 命令
celery -A ushow_nlp inspect conf
celery -A ushow_nlp inspect active
celery -A ushow_nlp inspect stats
```

---

### 方案 4: 增加超时时间

**如果网络延迟较高**:

```bash
# 使用 --timeout 参数增加超时时间
celery -A ushow_nlp inspect conf --timeout=10

# 或在 Python 中
from ushow_nlp import app
inspect = app.control.inspect(timeout=10)
conf = inspect.conf()
```

---

### 方案 5: 检查 Kubernetes 环境配置

**在 Kubernetes 中常见问题**:

1. **Redis 服务不可达**
   ```bash
   # 检查 Redis Service
   kubectl get svc | grep redis
   
   # 检查 Redis Pod
   kubectl get pods | grep redis
   
   # 检查网络策略
   kubectl get networkpolicies
   ```

2. **环境变量未设置**
   ```bash
   # 检查 Pod 环境变量
   kubectl exec <pod-name> -- env | grep -i redis
   
   # 检查 ConfigMap
   kubectl get configmap
   kubectl describe configmap <configmap-name>
   ```

3. **DNS 解析问题**
   ```bash
   # 在 Pod 中测试 DNS
   kubectl exec <pod-name> -- nslookup <redis-service>
   ```

---

## 📋 快速排查清单

按顺序检查以下项目：

- [ ] **Worker 是否运行？**
  ```bash
  ps aux | grep celery
  ```

- [ ] **Redis/Broker 是否可达？**
  ```bash
  redis-cli ping
  ```

- [ ] **应用名称是否一致？**
  ```bash
  # Worker: celery -A ushow_nlp worker
  # Client: celery -A ushow_nlp inspect conf
  ```

- [ ] **Broker URL 配置是否正确？**
  ```python
  from ushow_nlp import app
  print(app.conf.broker_url)
  ```

- [ ] **网络连接是否正常？**
  ```bash
  telnet <redis-host> <redis-port>
  ```

- [ ] **Worker 日志是否有错误？**
  ```bash
  tail -f /path/to/celery.log
  ```

- [ ] **环境变量是否设置？**
  ```bash
  env | grep -i redis
  ```

---

## 🔧 调试命令

### 1. 测试 Celery 连接（Python）

```python
from ushow_nlp import app

# 创建 inspect 对象
inspect = app.control.inspect(timeout=5)

# 测试连接
try:
    active = inspect.active()
    if active:
        print("✅ 检测到 Worker:", list(active.keys()))
    else:
        print("⚠️  未检测到 Worker")
except Exception as e:
    print(f"❌ 连接错误: {e}")
```

### 2. 检查 Worker 注册

```bash
# 检查已注册的任务
celery -A ushow_nlp inspect registered

# 检查 Worker 统计
celery -A ushow_nlp inspect stats

# 检查活动队列
celery -A ushow_nlp inspect active_queues
```

### 3. 测试任务提交

```python
# 测试任务是否能提交
from ushow_nlp import app

# 提交一个测试任务
result = app.send_task('tasks.test_task', args=[1, 2])
print(f"任务 ID: {result.id}")

# 检查任务状态
print(f"任务状态: {result.state}")
```

---

## 🎯 针对 Kubernetes 环境的特殊检查

### 1. 检查 Service 和 Endpoints

```bash
# 检查 Redis Service
kubectl get svc redis
kubectl describe svc redis

# 检查 Endpoints
kubectl get endpoints redis
```

### 2. 检查 Pod 网络

```bash
# 在 Pod 中测试连接
kubectl exec -it <pod-name> -- redis-cli -h <redis-service> ping

# 检查 DNS
kubectl exec -it <pod-name> -- nslookup <redis-service>
```

### 3. 检查 ConfigMap 和 Secret

```bash
# 检查配置
kubectl get configmap
kubectl get secret

# 查看配置内容
kubectl get configmap <configmap-name> -o yaml
kubectl get secret <secret-name> -o yaml
```

### 4. 检查 Pod 环境变量

```bash
# 查看 Pod 环境变量
kubectl exec <pod-name> -- env | grep -i redis
kubectl exec <pod-name> -- env | grep -i celery
```

---

## 💡 常见问题解决

### 问题 1: Worker 在运行但 inspect 无法连接

**可能原因**: Worker 和 Client 使用不同的 Broker

**解决方案**:
```python
# 确保 Worker 和 Client 使用相同的 Broker URL
# 在应用配置中
app.conf.broker_url = 'redis://redis-service:6379/0'
```

### 问题 2: 在 Kubernetes 中 Redis 连接失败

**可能原因**: Service 名称或端口不正确

**解决方案**:
```python
# 使用 Kubernetes Service 名称
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')  # Service 名称
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
```

### 问题 3: 超时时间太短

**解决方案**:
```bash
# 增加超时时间
celery -A ushow_nlp inspect conf --timeout=10

# 或在代码中
inspect = app.control.inspect(timeout=10)
```

---

## 🚀 快速修复脚本

```bash
#!/bin/bash
# quick_fix.sh

echo "🔍 检查 Celery 状态..."

# 1. 检查 Worker
echo "1. 检查 Worker 进程..."
if pgrep -f "celery.*worker" > /dev/null; then
    echo "✅ Worker 正在运行"
else
    echo "❌ Worker 未运行，启动 Worker..."
    celery -A ushow_nlp worker --loglevel=info &
fi

# 2. 检查 Redis
echo "2. 检查 Redis 连接..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 连接正常"
else
    echo "❌ Redis 连接失败，请检查 Redis 配置"
fi

# 3. 测试 Inspect
echo "3. 测试 Celery Inspect..."
if celery -A ushow_nlp inspect conf --timeout=5 > /dev/null 2>&1; then
    echo "✅ Celery Inspect 正常"
else
    echo "❌ Celery Inspect 失败"
    echo "💡 请检查:"
    echo "   - Worker 是否运行"
    echo "   - Broker 连接配置"
    echo "   - 应用名称是否一致"
fi
```

---

## 📚 相关文档

- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 通用故障排查
- [DOCKER_REDIS.md](./DOCKER_REDIS.md) - Docker Redis 连接
- [CELERY_CONFIG.md](./CELERY_CONFIG.md) - Celery 配置详解

---

**按照以上步骤排查，大多数问题都能快速解决！** 🎯

