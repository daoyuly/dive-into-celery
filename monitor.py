"""
Celery 监控工具

用于监控 Celery 任务执行状态、Worker 状态等
"""

from celery_app import app
from celery.result import AsyncResult
import time


def get_task_info(task_id):
    """获取任务信息"""
    result = AsyncResult(task_id, app=app)
    
    info = {
        'task_id': task_id,
        'state': result.state,
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else None,
        'failed': result.failed() if result.ready() else None,
    }
    
    if result.ready():
        if result.successful():
            info['result'] = result.result
        elif result.failed():
            info['error'] = str(result.result)
    else:
        # 任务进行中，获取进度信息
        info['info'] = result.info
    
    return info


def monitor_task(task_id, interval=1):
    """监控任务执行"""
    print(f"开始监控任务: {task_id}")
    print("-" * 50)
    
    while True:
        info = get_task_info(task_id)
        
        print(f"\r状态: {info['state']}", end='')
        
        if isinstance(info.get('info'), dict):
            if 'percent' in info['info']:
                print(f" | 进度: {info['info']['percent']}%", end='')
            if 'step' in info['info']:
                print(f" | 步骤: {info['info']['step']}", end='')
        
        if info['ready']:
            print()  # 换行
            if info['successful']:
                print(f"任务成功完成！结果: {info.get('result')}")
            elif info['failed']:
                print(f"任务失败！错误: {info.get('error')}")
            break
        
        time.sleep(interval)
    
    return info


def get_worker_stats():
    """获取 Worker 统计信息"""
    inspect = app.control.inspect()
    
    # 活跃的 workers
    active = inspect.active()
    # 已注册的任务
    registered = inspect.registered()
    # Worker 统计
    stats = inspect.stats()
    
    return {
        'active': active,
        'registered': registered,
        'stats': stats
    }


def print_worker_stats():
    """打印 Worker 统计信息"""
    stats = get_worker_stats()
    
    print("=" * 50)
    print("Celery Worker 统计信息")
    print("=" * 50)
    
    if stats['active']:
        print("\n活跃的任务:")
        for worker, tasks in stats['active'].items():
            print(f"  {worker}: {len(tasks)} 个任务")
            for task in tasks:
                print(f"    - {task['name']} (ID: {task['id']})")
    
    if stats['registered']:
        print("\n已注册的任务:")
        for worker, tasks in stats['registered'].items():
            print(f"  {worker}: {len(tasks)} 个任务类型")
    
    if stats['stats']:
        print("\nWorker 统计:")
        for worker, worker_stats in stats['stats'].items():
            print(f"  {worker}:")
            print(f"    池大小: {worker_stats.get('pool', {}).get('max-concurrency', 'N/A')}")
            print(f"    已处理任务数: {worker_stats.get('total', {}).get('tasks.succeeded', 0)}")


if __name__ == '__main__':
    # 示例：监控任务
    # task_id = 'your-task-id-here'
    # monitor_task(task_id)
    
    # 打印 Worker 统计
    print_worker_stats()

