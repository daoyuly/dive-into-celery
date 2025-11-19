# 🐳 使用 Docker Redis 连接指南

## 快速开始

### 方式 1: 使用 Docker Compose（推荐）

1. **启动 Redis 容器**:
```bash
docker-compose up -d
```

2. **验证 Redis 运行**:
```bash
docker-compose ps
# 或
docker ps | grep redis
```

3. **测试连接**:
```bash
docker exec -it celery_redis redis-cli ping
# 应该返回: PONG
```

4. **直接使用**（无需修改配置）:
```bash
# 默认连接 localhost:6379，Docker 已映射到该端口
celery -A celery_app worker --loglevel=info
```

### 方式 2: 使用 Docker 命令

1. **启动 Redis 容器**:
```bash
docker run -d \
  --name celery_redis \
  -p 6379:6379 \
  redis:7-alpine
```

2. **验证运行**:
```bash
docker ps | grep redis
```

3. **测试连接**:
```bash
docker exec -it celery_redis redis-cli ping
```

## 连接方式说明

### 默认连接（localhost:6379）

如果 Docker Redis 映射到 `localhost:6379`，**无需修改配置**，直接使用：

```bash
celery -A celery_app worker --loglevel=info
```

### 使用环境变量

如果需要连接不同端口的 Redis 或带密码的 Redis：

```bash
# 连接不同端口
export REDIS_HOST=localhost
export REDIS_PORT=6380
celery -A celery_app worker --loglevel=info

# 连接带密码的 Redis
export REDIS_PASSWORD=your_password
celery -A celery_app worker --loglevel=info
```

### 直接修改配置

如果需要，也可以直接修改 `celery_app.py` 中的连接字符串：

```python
# 连接 Docker Redis（默认端口）
broker='redis://localhost:6379/0'

# 连接不同端口
broker='redis://localhost:6380/0'

# 连接带密码的 Redis
broker='redis://:password@localhost:6379/0'

# 连接远程 Redis
broker='redis://remote-host:6379/0'
```

## 常见场景

### 场景 1: 使用默认端口（6379）

```bash
# 启动 Docker Redis
docker run -d -p 6379:6379 --name celery_redis redis:7-alpine

# 直接使用，无需修改配置
celery -A celery_app worker --loglevel=info
```

### 场景 2: 使用自定义端口

```bash
# 启动 Docker Redis 映射到 6380 端口
docker run -d -p 6380:6379 --name celery_redis redis:7-alpine

# 使用环境变量
export REDIS_PORT=6380
celery -A celery_app worker --loglevel=info
```

### 场景 3: 使用带密码的 Redis

```bash
# 启动带密码的 Redis
docker run -d \
  -p 6379:6379 \
  --name celery_redis \
  redis:7-alpine \
  redis-server --requirepass your_password

# 使用环境变量
export REDIS_PASSWORD=your_password
celery -A celery_app worker --loglevel=info
```

### 场景 4: 持久化数据

```bash
# 使用 Docker Compose（已配置持久化）
docker-compose up -d

# 或使用 Docker 命令
docker run -d \
  -p 6379:6379 \
  -v redis_data:/data \
  --name celery_redis \
  redis:7-alpine \
  redis-server --appendonly yes
```

## 验证连接

### 方法 1: 使用 redis-cli

```bash
# 进入容器
docker exec -it celery_redis redis-cli

# 在 redis-cli 中
> ping
PONG
> keys *
(empty array)
```

### 方法 2: 使用 Python

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # 应该返回 True
```

### 方法 3: 启动 Celery Worker

如果 Worker 能正常启动并显示连接信息，说明连接成功：

```bash
celery -A celery_app worker --loglevel=info
```

应该看到：
```
[INFO/MainProcess] Connected to redis://localhost:6379/0
```

## 故障排查

### 问题 1: 无法连接 Redis

**检查 Redis 是否运行**:
```bash
docker ps | grep redis
```

**检查端口映射**:
```bash
docker port celery_redis
# 应该显示: 6379/tcp -> 0.0.0.0:6379
```

**检查防火墙**:
```bash
# macOS/Linux
netstat -an | grep 6379
```

### 问题 2: 连接被拒绝

**检查 Redis 容器日志**:
```bash
docker logs celery_redis
```

**重启 Redis 容器**:
```bash
docker restart celery_redis
```

### 问题 3: 密码错误

**检查密码配置**:
```bash
# 查看 Redis 配置
docker exec -it celery_redis redis-cli
> CONFIG GET requirepass
```

**使用正确的密码**:
```bash
export REDIS_PASSWORD=correct_password
```

## Docker Compose 使用说明

项目已包含 `docker-compose.yml` 文件，使用方式：

```bash
# 启动 Redis
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs redis

# 停止 Redis
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 生产环境建议

1. **使用密码保护**:
```yaml
command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
```

2. **使用数据卷持久化**:
```yaml
volumes:
  - redis_data:/data
```

3. **配置健康检查**:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

4. **限制资源使用**:
```yaml
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

## 总结

- ✅ **默认配置**: Docker Redis 映射到 `localhost:6379` 可直接使用
- ✅ **环境变量**: 使用 `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` 灵活配置
- ✅ **Docker Compose**: 使用 `docker-compose.yml` 一键启动
- ✅ **持久化**: 数据保存在 Docker 卷中，容器重启不丢失

---

**现在你可以轻松使用 Docker Redis 了！** 🎉

