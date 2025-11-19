# Examples 目录说明

## 运行示例

### 方式 1: 直接运行（推荐）

```bash
# 从项目根目录运行
cd /Users/umu/Documents/tech/my-github/celery_learning

# 运行基础示例
python3 examples/basic_usage.py

# 运行高级示例
python3 examples/advanced_usage.py

# 运行实际工程示例
python3 examples/realworld_usage.py

# 运行 Worker 架构演示
python3 examples/worker_architecture_demo.py
```

### 方式 2: 使用 Python 模块方式

```bash
# 从项目根目录运行
python3 -m examples.basic_usage
python3 -m examples.advanced_usage
python3 -m examples.realworld_usage
```

### 方式 3: 使用交互式菜单

```bash
# 从项目根目录运行
python3 main.py
```

## 注意事项

1. **确保依赖已安装**:
   ```bash
   uv sync
   # 或
   pip install celery redis
   ```

2. **确保 Redis 正在运行**:
   ```bash
   # 使用 Docker
   docker-compose up -d
   
   # 或验证本地 Redis
   redis-cli ping
   ```

3. **确保 Celery Worker 正在运行**:
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

## 文件说明

- `basic_usage.py`: 基础用法示例（简单任务、进度跟踪等）
- `advanced_usage.py`: 高级用法示例（任务链、任务组、Chord 等）
- `realworld_usage.py`: 实际工程用法示例（邮件、图片处理等）
- `worker_architecture_demo.py`: Worker 架构和超时机制演示

## 导入路径说明

所有示例文件都包含路径处理代码，可以直接运行：

```python
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

这样无论从哪个目录运行，都能正确导入项目模块。

