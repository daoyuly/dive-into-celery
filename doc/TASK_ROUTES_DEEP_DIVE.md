# 🔀 Task Routes 深入解析

## 📋 什么是 Task Routes？

`task_routes` 是 Celery 的**任务路由配置**，用于将不同类型的任务路由到不同的队列。它实现了任务的**分类、隔离和优先级处理**。

---

## 🎯 核心作用

### 1. 任务隔离（Task Isolation）

将不同类型的任务分配到不同的队列，实现任务隔离：

```python
task_routes={
    'tasks.email.*': {'queue': 'email'},      # 邮件任务
    'tasks.image.*': {'queue': 'image'},      # 图片处理任务
    'tasks.data.*': {'queue': 'data'},        # 数据处理任务
}
```

**好处**:
- 一个队列的任务阻塞不会影响其他队列
- 可以针对不同队列使用不同的 Worker 配置
- 便于监控和管理

### 2. 优先级处理（Priority Handling）

为不同类型的任务设置不同的优先级：

```python
task_routes={
    'tasks.critical.*': {
        'queue': 'critical',
        'priority': 9,  # 高优先级
    },
    'tasks.normal.*': {
        'queue': 'normal',
        'priority': 5,  # 普通优先级
    },
    'tasks.low.*': {
        'queue': 'low',
        'priority': 1,  # 低优先级
    },
}
```

### 3. 资源分配（Resource Allocation）

根据任务特性分配不同的 Worker：

```python
task_routes={
    'tasks.cpu_intensive.*': {'queue': 'cpu'},    # CPU 密集型
    'tasks.io_intensive.*': {'queue': 'io'},      # I/O 密集型
}
```

---

## 🔧 工作机制

### 1. 路由匹配过程

```
任务提交 → 检查 task_routes → 匹配路由规则 → 发送到指定队列
```

**详细流程**:

```
1. 任务提交
   task.delay(args)

2. Celery 查找路由配置
   app.conf.task_routes

3. 匹配任务名称
   'tasks.basic_tasks.add' → 匹配 'tasks.basic_tasks.*'

4. 应用路由规则
   {'queue': 'basic'}

5. 发送到指定队列
   Redis: basic 队列

6. Worker 从队列获取
   celery -A celery_app worker --queues=basic
```

### 2. 路由匹配规则

#### 模式匹配语法

```python
task_routes={
    # 精确匹配
    'tasks.basic_tasks.add': {'queue': 'basic'},
    
    # 通配符匹配（最常用）
    'tasks.basic_tasks.*': {'queue': 'basic'},        # 匹配所有 basic_tasks 下的任务
    'tasks.*.email': {'queue': 'email'},              # 匹配所有 email 任务
    '*.critical.*': {'queue': 'critical'},             # 匹配所有包含 critical 的任务
    
    # 正则表达式匹配（高级）
    'tasks\.(basic|advanced)\.*': {'queue': 'general'},  # 需要配置 task_routes 为函数
}
```

#### 匹配优先级

1. **精确匹配** > **通配符匹配**
2. **更具体的模式** > **更通用的模式**
3. **第一个匹配**（如果多个规则匹配，使用第一个）

**示例**:
```python
task_routes={
    'tasks.basic_tasks.add': {'queue': 'specific'},    # 精确匹配，优先级最高
    'tasks.basic_tasks.*': {'queue': 'general'},      # 通配符匹配
    'tasks.*': {'queue': 'default'},                   # 最通用的匹配
}
```

### 3. 路由配置选项

```python
task_routes={
    'tasks.my_task': {
        # 队列配置
        'queue': 'my_queue',           # 队列名称（必需）
        
        # 交换机配置（RabbitMQ）
        'exchange': 'tasks',           # 交换机名称
        'exchange_type': 'direct',     # 交换机类型
        'routing_key': 'my_task',      # 路由键
        
        # 优先级
        'priority': 9,                 # 0-9，数字越大优先级越高
        
        # 其他选项
        'delivery_mode': 2,            # 持久化（2=持久化，1=非持久化）
    },
}
```

---

## 🏗️ 实际应用场景

### 场景 1: 按功能分类

```python
task_routes={
    # 邮件服务
    'tasks.email.*': {'queue': 'email'},
    
    # 图片处理
    'tasks.image.*': {'queue': 'image'},
    
    # 数据导入导出
    'tasks.data.*': {'queue': 'data'},
    
    # 报告生成
    'tasks.report.*': {'queue': 'report'},
}
```

**Worker 启动**:
```bash
# 只处理邮件任务
celery -A celery_app worker --queues=email

# 只处理图片任务
celery -A celery_app worker --queues=image

# 处理多个队列
celery -A celery_app worker --queues=email,image,data
```

### 场景 2: 按优先级分类

```python
task_routes={
    # 紧急任务（高优先级）
    'tasks.critical.*': {
        'queue': 'critical',
        'priority': 9,
    },
    
    # 普通任务
    'tasks.normal.*': {
        'queue': 'normal',
        'priority': 5,
    },
    
    # 后台任务（低优先级）
    'tasks.background.*': {
        'queue': 'background',
        'priority': 1,
    },
}
```

### 场景 3: 按资源需求分类

```python
task_routes={
    # CPU 密集型任务（需要更多 CPU）
    'tasks.cpu_intensive.*': {'queue': 'cpu'},
    
    # I/O 密集型任务（需要更多内存）
    'tasks.io_intensive.*': {'queue': 'io'},
    
    # 混合任务
    'tasks.mixed.*': {'queue': 'mixed'},
}
```

**Worker 配置**:
```bash
# CPU 密集型任务：更多进程，较少并发
celery -A celery_app worker --queues=cpu --concurrency=8

# I/O 密集型任务：使用协程，更多并发
celery -A celery_app worker --queues=io --pool=gevent --concurrency=100
```

### 场景 4: 按环境分类

```python
task_routes={
    # 生产环境任务
    'tasks.production.*': {'queue': 'production'},
    
    # 测试环境任务
    'tasks.test.*': {'queue': 'test'},
    
    # 开发环境任务
    'tasks.development.*': {'queue': 'development'},
}
```

---

## 🔍 高级用法

### 1. 使用函数进行动态路由

```python
def route_task(name, args, kwargs, options, task=None, **kw):
    """动态路由函数"""
    if 'email' in name:
        return {'queue': 'email'}
    elif 'image' in name:
        return {'queue': 'image'}
    elif 'critical' in name:
        return {'queue': 'critical', 'priority': 9}
    else:
        return {'queue': 'default'}

app.conf.task_routes = route_task
```

### 2. 基于任务参数路由

```python
def route_by_priority(name, args, kwargs, options, task=None, **kw):
    """根据任务参数动态路由"""
    # 从 kwargs 中获取优先级
    priority = kwargs.get('priority', 'normal')
    
    if priority == 'high':
        return {'queue': 'high_priority', 'priority': 9}
    elif priority == 'low':
        return {'queue': 'low_priority', 'priority': 1}
    else:
        return {'queue': 'normal', 'priority': 5}

app.conf.task_routes = route_by_priority
```

### 3. 基于 Worker 负载路由

```python
def route_by_load(name, args, kwargs, options, task=None, **kw):
    """根据 Worker 负载动态路由"""
    # 检查各个队列的长度
    # 选择负载最小的队列
    # （需要额外的监控逻辑）
    return {'queue': 'least_loaded_queue'}

app.conf.task_routes = route_by_load
```

### 4. 组合路由规则

```python
# 方式 1: 在配置中组合
task_routes={
    'tasks.critical.email.*': {
        'queue': 'critical_email',
        'priority': 9,
    },
    'tasks.normal.email.*': {
        'queue': 'normal_email',
        'priority': 5,
    },
}

# 方式 2: 使用函数组合
def combined_route(name, args, kwargs, options, task=None, **kw):
    route = {}
    
    # 根据功能分类
    if 'email' in name:
        route['queue'] = 'email'
    elif 'image' in name:
        route['queue'] = 'image'
    
    # 根据优先级
    if 'critical' in name:
        route['priority'] = 9
    elif 'normal' in name:
        route['priority'] = 5
    
    return route if route else None
```

---

## 📊 路由匹配示例

### 示例 1: 基础路由

```python
# 配置
task_routes={
    'tasks.basic_tasks.*': {'queue': 'basic'},
    'tasks.advanced_tasks.*': {'queue': 'advanced'},
}

# 任务
tasks.basic_tasks.add          → basic 队列
tasks.basic_tasks.multiply     → basic 队列
tasks.advanced_tasks.fetch_data → advanced 队列
```

### 示例 2: 优先级路由

```python
# 配置
task_routes={
    'tasks.critical.*': {'queue': 'critical', 'priority': 9},
    'tasks.normal.*': {'queue': 'normal', 'priority': 5},
}

# 任务
tasks.critical.backup          → critical 队列，优先级 9
tasks.normal.cleanup          → normal 队列，优先级 5
```

### 示例 3: 复杂路由

```python
# 配置
task_routes={
    'tasks.email.send': {'queue': 'email_send'},
    'tasks.email.*': {'queue': 'email'},
    'tasks.*.critical': {'queue': 'critical'},
    'tasks.*': {'queue': 'default'},
}

# 任务匹配
tasks.email.send               → email_send（精确匹配）
tasks.email.verify             → email（通配符匹配）
tasks.data.critical            → critical（通配符匹配）
tasks.other.task               → default（默认匹配）
```

---

## 🛠️ 实际配置示例

### 完整配置示例

```python
app.conf.update(
    # 任务路由配置
    task_routes={
        # 高优先级任务
        'tasks.critical.*': {
            'queue': 'critical',
            'priority': 9,
        },
        
        # 邮件任务
        'tasks.email.*': {
            'queue': 'email',
            'priority': 7,
        },
        
        # 图片处理任务
        'tasks.image.*': {
            'queue': 'image',
            'priority': 5,
        },
        
        # 数据任务
        'tasks.data.*': {
            'queue': 'data',
            'priority': 5,
        },
        
        # 后台任务
        'tasks.background.*': {
            'queue': 'background',
            'priority': 1,
        },
        
        # 默认路由
        'tasks.*': {
            'queue': 'default',
            'priority': 5,
        },
    },
    
    # 队列配置
    task_default_queue='default',
    task_default_exchange='tasks',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
)
```

### Worker 启动配置

```bash
# 只处理高优先级任务
celery -A celery_app worker --queues=critical --concurrency=4

# 处理邮件和图片任务
celery -A celery_app worker --queues=email,image --concurrency=8

# 处理所有队列
celery -A celery_app worker --queues=critical,email,image,data,background,default
```

---

## 🔍 调试和验证

### 1. 查看路由配置

```python
from celery_app import app

# 查看路由配置
print(app.conf.task_routes)
```

### 2. 测试路由匹配

```python
from celery_app import app

# 测试任务路由
task_name = 'tasks.basic_tasks.add'
route = app.conf.task_routes.get(task_name)

# 或者使用 Celery 的路由函数
from celery.app.routes import route_task
route = route_task(task_name, [], {}, {}, task=None)
print(f"任务 {task_name} 路由到: {route}")
```

### 3. 查看队列内容

```bash
# 使用 Redis CLI
redis-cli
> LLEN basic
> LRANGE basic 0 -1

# 或使用监控工具
python3 queue_monitor.py
python3 redis_queue_viewer.py
```

### 4. 验证 Worker 队列

```python
from celery_app import app

# 检查 Worker 监听的队列
inspect = app.control.inspect()
active_queues = inspect.active_queues()
print(active_queues)
```

---

## ⚠️ 常见问题和解决方案

### 问题 1: 任务没有路由到指定队列

**原因**:
- 路由规则不匹配
- Worker 没有监听该队列
- 队列名称拼写错误

**解决方案**:
```python
# 1. 检查路由规则
print(app.conf.task_routes)

# 2. 检查任务名称
print(task.name)  # 确保任务名称匹配路由规则

# 3. 检查 Worker 启动命令
# celery -A celery_app worker --queues=your_queue
```

### 问题 2: 多个路由规则匹配

**原因**: 多个规则都匹配同一个任务

**解决方案**:
- 使用更具体的规则
- 调整规则顺序（第一个匹配的规则生效）

### 问题 3: 路由到不存在的队列

**原因**: Worker 没有监听该队列

**解决方案**:
```bash
# 确保 Worker 监听所有需要的队列
celery -A celery_app worker --queues=queue1,queue2,queue3
```

---

## 🎯 最佳实践

### 1. 使用清晰的命名规范

```python
# ✅ 好的命名
'tasks.email.send': {'queue': 'email'}
'tasks.image.process': {'queue': 'image'}

# ❌ 不好的命名
'task1': {'queue': 'q1'}
'task2': {'queue': 'q2'}
```

### 2. 使用通配符简化配置

```python
# ✅ 使用通配符
'tasks.email.*': {'queue': 'email'}

# ❌ 为每个任务单独配置
'tasks.email.send': {'queue': 'email'}
'tasks.email.verify': {'queue': 'email'}
'tasks.email.cleanup': {'queue': 'email'}
```

### 3. 设置默认路由

```python
task_routes={
    'tasks.special.*': {'queue': 'special'},
    'tasks.*': {'queue': 'default'},  # 默认路由
}
```

### 4. 根据实际需求调整

- **高并发场景**: 使用多个队列，分散负载
- **优先级场景**: 使用优先级队列
- **资源隔离**: 按资源需求分类

---

## 📚 总结

### Task Routes 的核心价值

1. **任务隔离**: 不同类型的任务互不影响
2. **优先级处理**: 重要任务优先执行
3. **资源分配**: 根据任务特性分配资源
4. **可扩展性**: 易于添加新的任务类型

### 关键要点

- ✅ 路由规则使用模式匹配（通配符 `*`）
- ✅ 第一个匹配的规则生效
- ✅ Worker 必须监听相应的队列
- ✅ 可以使用函数实现动态路由
- ✅ 路由配置影响任务分发，不影响任务执行

---

**通过合理配置 task_routes，你可以构建一个高效、可扩展的 Celery 任务系统！** 🚀

