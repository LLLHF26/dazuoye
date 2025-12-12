"""
智能问答API
===========
提供问答机器人接口，学生可以提问关于课程安排、作业要求等问题。
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.qa_service import QAService
from app.models.user import User

qa_bp = Blueprint('qa', __name__)

# 初始化问答服务（单例模式）
_qa_service = None

def get_qa_service():
    """获取问答服务实例（单例）"""
    global _qa_service
    if _qa_service is None:
        _qa_service = QAService()
    return _qa_service


@qa_bp.route('/ask', methods=['POST'])
@jwt_required(optional=True)
def ask_question():
    """
    提问接口
    
    请求体:
        {
            "question": "课程什么时候开始？",
            "top_k": 3  # 可选，返回前k个最相关的答案，默认3
        }
    
    返回:
        {
            "answer": "答案内容",
            "confidence": 0.85,
            "matched_question": "匹配的问题",
            "category": "课程安排",
            "top_matches": [...]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': '缺少question字段'}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        top_k = data.get('top_k', 3)
        if not isinstance(top_k, int) or top_k < 1:
            top_k = 3
        
        # 获取问答服务并回答问题
        qa_service = get_qa_service()
        result = qa_service.ask(question, top_k=top_k)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'处理问题失败: {str(e)}'}), 500


@qa_bp.route('/categories', methods=['GET'])
@jwt_required(optional=True)
def get_categories():
    """
    获取所有问题分类
    
    返回:
        {
            "categories": ["课程安排", "作业要求", ...]
        }
    """
    try:
        qa_service = get_qa_service()
        categories = qa_service.get_categories()
        
        return jsonify({
            'categories': categories
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'获取分类失败: {str(e)}'}), 500


@qa_bp.route('/categories/<category_name>/qa-pairs', methods=['GET'])
@jwt_required(optional=True)
def get_qa_pairs_by_category(category_name):
    """
    获取指定分类的所有问答对
    
    返回:
        {
            "category": "课程安排",
            "qa_pairs": [
                {
                    "question": "问题",
                    "answer": "答案",
                    "keywords": ["关键词1", "关键词2"]
                },
                ...
            ]
        }
    """
    try:
        qa_service = get_qa_service()
        qa_pairs = qa_service.get_qa_pairs_by_category(category_name)
        
        if not qa_pairs:
            return jsonify({
                'error': f'分类"{category_name}"不存在或没有问答对'
            }), 404
        
        return jsonify({
            'category': category_name,
            'qa_pairs': qa_pairs
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'获取问答对失败: {str(e)}'}), 500


@qa_bp.route('/qa-pairs', methods=['POST'])
@jwt_required()
def add_qa_pair():
    """
    添加新的问答对（需要登录，建议仅教师/管理员使用）
    
    请求体:
        {
            "category": "课程安排",
            "question": "新问题",
            "answer": "新答案",
            "keywords": ["关键词1", "关键词2"]  # 可选
        }
    
    返回:
        {
            "message": "问答对添加成功",
            "qa_pair": {...}
        }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 可选：限制只有教师或管理员可以添加
        # if user.role not in ['teacher', 'admin']:
        #     return jsonify({'error': '无权添加问答对'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['category', 'question', 'answer']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        category = data['category'].strip()
        question = data['question'].strip()
        answer = data['answer'].strip()
        keywords = data.get('keywords', [])
        
        if not question or not answer:
            return jsonify({'error': '问题和答案不能为空'}), 400
        
        # 添加问答对
        qa_service = get_qa_service()
        qa_service.add_qa_pair(category, question, answer, keywords)
        
        return jsonify({
            'message': '问答对添加成功',
            'qa_pair': {
                'category': category,
                'question': question,
                'answer': answer,
                'keywords': keywords
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'添加问答对失败: {str(e)}'}), 500


@qa_bp.route('/train', methods=['POST'])
@jwt_required()
def train_model():
    """
    训练PyTorch模型（需要登录，建议仅管理员使用）
    
    请求体:
        {
            "epochs": 10,  # 可选，训练轮数，默认10
            "batch_size": 32,  # 可选，批次大小，默认32
            "lr": 0.001  # 可选，学习率，默认0.001
        }
    
    返回:
        {
            "message": "模型训练完成",
            "epochs": 10,
            "training_samples": 100
        }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 可选：限制只有管理员可以训练模型
        # if user.role != 'admin':
        #     return jsonify({'error': '无权训练模型'}), 403
        
        data = request.get_json() or {}
        epochs = data.get('epochs', 10)
        batch_size = data.get('batch_size', 32)
        lr = data.get('lr', 0.001)
        
        qa_service = get_qa_service()
        qa_service.train_model(epochs=epochs, batch_size=batch_size, lr=lr)
        
        return jsonify({
            'message': '模型训练完成',
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': lr,
            'training_samples': len(qa_service.processed_qa_pairs)
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'训练失败: {str(e)}'}), 500


@qa_bp.route('/health', methods=['GET'])
def health_check():
    """
    问答服务健康检查
    
    返回:
        {
            "status": "ok",
            "qa_pairs_count": 20,
            "pytorch_enabled": true
        }
    """
    try:
        qa_service = get_qa_service()
        qa_pairs_count = len(qa_service.processed_qa_pairs)
        
        return jsonify({
            'status': 'ok',
            'qa_pairs_count': qa_pairs_count,
            'pytorch_enabled': qa_service.use_pytorch
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

