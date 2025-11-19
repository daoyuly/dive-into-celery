"""
实际工程用法示例

演示在实际工程中如何使用 Celery
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tasks.realworld_tasks import (
    send_email,
    process_image,
    import_data,
    export_data,
    generate_report,
    cleanup_old_files
)
import time


def example_send_email():
    """邮件发送示例"""
    print("=" * 50)
    print("示例1: 发送邮件")
    print("=" * 50)
    
    result = send_email.delay(
        to_email='user@example.com',
        subject='欢迎使用我们的服务',
        body='这是一封测试邮件，感谢您使用我们的服务！'
    )
    
    print(f"邮件任务已提交，ID: {result.id}")
    email_result = result.get(timeout=30)
    print(f"邮件发送结果: {email_result}\n")


def example_process_image():
    """图片处理示例"""
    print("=" * 50)
    print("示例2: 图片处理")
    print("=" * 50)
    
    result = process_image.delay(
        image_path='uploads/photo.jpg',
        operations=['resize', 'crop', 'filter', 'watermark']
    )
    
    print(f"图片处理任务已提交，ID: {result.id}")
    
    # 跟踪进度
    while not result.ready():
        info = result.info
        if isinstance(info, dict) and 'percent' in info:
            print(f"处理进度: {info['percent']}% - {info.get('operation', '')}")
        time.sleep(1)
    
    print(f"图片处理完成: {result.get()}\n")


def example_import_data():
    """数据导入示例"""
    print("=" * 50)
    print("示例3: 数据导入")
    print("=" * 50)
    
    result = import_data.delay(
        file_path='data/users.csv',
        batch_size=100
    )
    
    print(f"数据导入任务已提交，ID: {result.id}")
    
    # 跟踪进度
    while not result.ready():
        info = result.info
        if isinstance(info, dict) and 'percent' in info:
            print(f"导入进度: {info['percent']}% ({info.get('processed', 0)}/{info.get('total', 0)})")
        time.sleep(1)
    
    print(f"数据导入完成: {result.get()}\n")


def example_export_data():
    """数据导出示例"""
    print("=" * 50)
    print("示例4: 数据导出")
    print("=" * 50)
    
    result = export_data.delay(
        query={'status': 'active', 'date': '2024-01-01'},
        output_format='json'
    )
    
    print(f"数据导出任务已提交，ID: {result.id}")
    
    # 跟踪进度
    while not result.ready():
        info = result.info
        if isinstance(info, dict) and 'percent' in info:
            print(f"导出进度: {info['percent']}%")
        time.sleep(0.5)
    
    print(f"数据导出完成: {result.get()}\n")


def example_generate_report():
    """报告生成示例"""
    print("=" * 50)
    print("示例5: 生成报告")
    print("=" * 50)
    
    result = generate_report.delay(
        report_type='daily',
        date_range={'start': '2024-01-01', 'end': '2024-01-31'}
    )
    
    print(f"报告生成任务已提交，ID: {result.id}")
    
    # 跟踪进度
    while not result.ready():
        info = result.info
        if isinstance(info, dict) and 'step' in info:
            print(f"当前步骤: {info['step']} ({info.get('percent', 0)}%)")
        time.sleep(1)
    
    print(f"报告生成完成: {result.get()}\n")


def example_batch_emails():
    """批量发送邮件示例"""
    print("=" * 50)
    print("示例6: 批量发送邮件")
    print("=" * 50)
    
    emails = [
        {'to': 'user1@example.com', 'subject': '通知1', 'body': '内容1'},
        {'to': 'user2@example.com', 'subject': '通知2', 'body': '内容2'},
        {'to': 'user3@example.com', 'subject': '通知3', 'body': '内容3'},
    ]
    
    # 并行发送多封邮件
    from celery import group
    job = group(
        send_email.s(email['to'], email['subject'], email['body'])
        for email in emails
    )
    
    result = job.apply_async()
    print(f"批量邮件任务已提交")
    print(f"发送结果: {result.get(timeout=60)}\n")


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Celery 实际工程用法示例")
    print("=" * 50 + "\n")
    
    # 运行示例
    example_send_email()
    example_process_image()
    example_import_data()
    example_export_data()
    example_generate_report()
    example_batch_emails()
    
    print("所有实际工程示例执行完成！")

