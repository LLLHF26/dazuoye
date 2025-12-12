"""
训练QA模型的脚本
===============
使用此脚本可以训练PyTorch模型用于智能问答系统
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.qa_service import QAService

def main():
    """训练模型的主函数"""
    print("=" * 50)
    print("开始训练QA模型")
    print("=" * 50)
    
    # 初始化QA服务
    qa_service = QAService()
    
    print(f"知识库包含 {len(qa_service.processed_qa_pairs)} 个问答对")
    
    # 训练模型
    try:
        qa_service.train_model(
            epochs=20,  # 训练轮数
            batch_size=32,  # 批次大小
            lr=0.001  # 学习率
        )
        print("\n" + "=" * 50)
        print("模型训练完成！")
        print("=" * 50)
    except Exception as e:
        print(f"\n训练失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

