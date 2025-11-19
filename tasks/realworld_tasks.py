"""
实际工程任务示例

这个模块展示了 Celery 在实际工程中的应用：
1. 图片处理任务
2. 邮件发送任务
3. 数据导入/导出任务
4. 文件处理任务
"""

from celery_app import app
import time
import os
from datetime import datetime
import json


@app.task(name='tasks.realworld_tasks.send_email', bind=True, max_retries=3)
def send_email(self, to_email, subject, body):
    """
    发送邮件任务（模拟）
    
    在实际工程中，这里会调用真实的邮件服务（如 SMTP、SendGrid、AWS SES 等）
    
    参数:
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 邮件内容
    """
    print(f"[邮件任务] 发送邮件到 {to_email}")
    print(f"主题: {subject}")
    print(f"内容: {body[:50]}...")
    
    # 模拟邮件发送（实际应该调用邮件服务）
    time.sleep(2)
    
    # 模拟10%的失败率
    import random
    if random.random() < 0.1:
        print("邮件发送失败，准备重试...")
        raise self.retry(countdown=5, exc=Exception("邮件服务暂时不可用"))
    
    print(f"[邮件任务] 邮件发送成功到 {to_email}")
    return {
        'status': 'success',
        'to': to_email,
        'subject': subject,
        'sent_at': datetime.now().isoformat()
    }


@app.task(name='tasks.realworld_tasks.process_image', bind=True)
def process_image(self, image_path, operations):
    """
    图片处理任务（模拟）
    
    在实际工程中，这里会使用 PIL/Pillow、OpenCV 等库进行真实的图片处理
    
    参数:
        image_path: 图片路径
        operations: 处理操作列表，如 ['resize', 'crop', 'filter']
    """
    print(f"[图片处理] 处理图片: {image_path}")
    print(f"操作: {operations}")
    
    # 模拟图片处理
    processed_images = []
    total_ops = len(operations)
    
    for i, op in enumerate(operations):
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_ops,
                'operation': op,
                'percent': int((i + 1) / total_ops * 100)
            }
        )
        
        print(f"执行操作: {op} ({i + 1}/{total_ops})")
        time.sleep(1)  # 模拟处理时间
        
        processed_images.append(f"{image_path}_{op}.jpg")
    
    result = {
        'original': image_path,
        'processed': processed_images,
        'operations': operations,
        'completed_at': datetime.now().isoformat()
    }
    
    print(f"[图片处理] 处理完成，生成 {len(processed_images)} 个文件")
    return result


@app.task(name='tasks.realworld_tasks.import_data', bind=True)
def import_data(self, file_path, batch_size=100):
    """
    数据导入任务
    
    模拟从文件（CSV、JSON等）导入数据到数据库
    
    参数:
        file_path: 数据文件路径
        batch_size: 每批处理的数据量
    """
    print(f"[数据导入] 开始导入文件: {file_path}")
    
    # 模拟读取文件
    total_records = 1000  # 假设文件有1000条记录
    processed = 0
    
    while processed < total_records:
        # 读取一批数据
        batch = min(batch_size, total_records - processed)
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'processed': processed,
                'total': total_records,
                'percent': int(processed / total_records * 100),
                'current_batch': batch
            }
        )
        
        # 模拟数据处理和数据库插入
        print(f"处理批次: {processed + 1}-{processed + batch}/{total_records}")
        time.sleep(0.5)
        
        processed += batch
    
    result = {
        'file': file_path,
        'total_records': total_records,
        'imported_at': datetime.now().isoformat(),
        'status': 'success'
    }
    
    print(f"[数据导入] 导入完成，共 {total_records} 条记录")
    return result


@app.task(name='tasks.realworld_tasks.export_data', bind=True)
def export_data(self, query, output_format='json'):
    """
    数据导出任务
    
    从数据库查询数据并导出到文件
    
    参数:
        query: 查询条件
        output_format: 输出格式（json, csv, excel）
    """
    print(f"[数据导出] 开始导出数据")
    print(f"查询条件: {query}")
    print(f"输出格式: {output_format}")
    
    # 模拟数据查询和导出
    total_records = 500
    exported = 0
    
    while exported < total_records:
        batch_size = 50
        batch = min(batch_size, total_records - exported)
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'exported': exported,
                'total': total_records,
                'percent': int(exported / total_records * 100),
                'format': output_format
            }
        )
        
        print(f"导出批次: {exported + 1}-{exported + batch}/{total_records}")
        time.sleep(0.3)
        
        exported += batch
    
    output_file = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
    
    result = {
        'output_file': output_file,
        'total_records': total_records,
        'format': output_format,
        'exported_at': datetime.now().isoformat()
    }
    
    print(f"[数据导出] 导出完成: {output_file}")
    return result


@app.task(name='tasks.realworld_tasks.generate_report', bind=True)
def generate_report(self, report_type, date_range):
    """
    生成报告任务
    
    参数:
        report_type: 报告类型（daily, weekly, monthly）
        date_range: 日期范围
    """
    print(f"[报告生成] 生成 {report_type} 报告")
    print(f"日期范围: {date_range}")
    
    # 模拟报告生成步骤
    steps = [
        '收集数据',
        '数据清洗',
        '数据分析',
        '生成图表',
        '生成PDF',
    ]
    
    for i, step in enumerate(steps):
        self.update_state(
            state='PROGRESS',
            meta={
                'step': step,
                'current': i + 1,
                'total': len(steps),
                'percent': int((i + 1) / len(steps) * 100)
            }
        )
        
        print(f"执行步骤: {step} ({i + 1}/{len(steps)})")
        time.sleep(1)
    
    report_file = f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    result = {
        'report_type': report_type,
        'report_file': report_file,
        'date_range': date_range,
        'generated_at': datetime.now().isoformat()
    }
    
    print(f"[报告生成] 报告生成完成: {report_file}")
    return result


@app.task(name='tasks.realworld_tasks.cleanup_old_files', bind=True)
def cleanup_old_files(self, directory, days_old=30):
    """
    清理旧文件任务
    
    参数:
        directory: 要清理的目录
        days_old: 删除多少天前的文件
    """
    print(f"[文件清理] 清理目录: {directory}")
    print(f"删除 {days_old} 天前的文件")
    
    # 模拟文件清理
    files_to_delete = 50
    deleted = 0
    
    for i in range(files_to_delete):
        self.update_state(
            state='PROGRESS',
            meta={
                'deleted': deleted,
                'total': files_to_delete,
                'percent': int(deleted / files_to_delete * 100)
            }
        )
        
        print(f"删除文件 {i + 1}/{files_to_delete}")
        time.sleep(0.1)
        deleted += 1
    
    result = {
        'directory': directory,
        'files_deleted': deleted,
        'days_old': days_old,
        'cleaned_at': datetime.now().isoformat()
    }
    
    print(f"[文件清理] 清理完成，删除了 {deleted} 个文件")
    return result

