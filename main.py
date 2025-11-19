"""
Celery 学习项目主入口

这个文件提供了快速开始 Celery 学习的入口点
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("🎯 Celery 学习项目 - 主菜单")
    print("=" * 60)
    print("\n请选择要运行的示例：")
    print("1. 基础用法示例")
    print("2. 高级用法示例")
    print("3. 实际工程用法示例")
    print("4. 查看 Worker 状态")
    print("5. 退出")
    print("\n" + "-" * 60)


def main():
    """主函数"""
    show_menu()
    
    while True:
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == '1':
                print("\n🚀 运行基础用法示例...")
                from examples.basic_usage import (
                    example_simple_task,
                    example_task_with_wait,
                    example_batch_processing,
                    example_long_running_with_progress
                )
                example_simple_task()
                example_task_with_wait()
                example_batch_processing()
                example_long_running_with_progress()
                print("\n✅ 基础示例执行完成！")
                
            elif choice == '2':
                print("\n🚀 运行高级用法示例...")
                from examples.advanced_usage import (
                    example_task_chain,
                    example_task_group,
                    example_chord,
                    example_task_retry,
                    example_custom_retry,
                    example_complex_workflow
                )
                example_task_chain()
                example_task_group()
                example_chord()
                example_task_retry()
                example_custom_retry()
                example_complex_workflow()
                print("\n✅ 高级示例执行完成！")
                
            elif choice == '3':
                print("\n🚀 运行实际工程用法示例...")
                from examples.realworld_usage import (
                    example_send_email,
                    example_process_image,
                    example_import_data,
                    example_export_data,
                    example_generate_report,
                    example_batch_emails
                )
                example_send_email()
                example_process_image()
                example_import_data()
                example_export_data()
                example_generate_report()
                example_batch_emails()
                print("\n✅ 实际工程示例执行完成！")
                
            elif choice == '4':
                print("\n📊 查看 Worker 状态...")
                from monitor import print_worker_stats
                print_worker_stats()
                
            elif choice == '5':
                print("\n👋 再见！")
                break
                
            else:
                print("❌ 无效选项，请重新选择")
                
            # 询问是否继续
            if choice in ['1', '2', '3', '4']:
                continue_choice = input("\n是否继续？(y/n): ").strip().lower()
                if continue_choice != 'y':
                    show_menu()
                    
        except KeyboardInterrupt:
            print("\n\n👋 程序已中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            print("\n💡 提示: 请确保 Redis 正在运行，并且 Celery Worker 已启动")
            continue_choice = input("\n是否继续？(y/n): ").strip().lower()
            if continue_choice != 'y':
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已中断，再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

