"""
智能问答服务层
==============
基于NLTK进行文本预处理，PyTorch进行模型训练的课程问答机器人。
能够回答学生关于课程安排、作业要求等常见问题。
"""
import os
import json
import re
from typing import Dict, List, Tuple, Optional, Union
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from collections import Counter
import math

# 导入PyTorch模型管理器
try:
    from app.utils.qa_model import QAModelManager
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("警告: PyTorch未安装，将使用传统相似度计算方法")

# 确保NLTK数据已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

# 初始化工具
lemmatizer = WordNetLemmatizer()

# 获取停用词（支持中英文）
try:
    english_stopwords = set(stopwords.words('english'))
except:
    english_stopwords = set()

# 中文停用词（常用）
chinese_stopwords = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
}


class QAService:
    """问答服务类"""
    
    def __init__(self, knowledge_base_path: Optional[str] = None, use_pytorch: bool = True):
        """
        初始化问答服务
        
        Args:
            knowledge_base_path: 知识库文件路径，如果为None则使用默认路径
            use_pytorch: 是否使用PyTorch模型（如果可用）
        """
        if knowledge_base_path is None:
            # 默认知识库路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            knowledge_base_path = os.path.join(base_dir, 'app', 'data', 'knowledge_base.json')
        
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.processed_qa_pairs = self._process_knowledge_base()
        
        # 初始化PyTorch模型管理器
        self.use_pytorch = use_pytorch and PYTORCH_AVAILABLE
        self.model_manager = None
        if self.use_pytorch:
            try:
                self.model_manager = QAModelManager()
                # 尝试加载已训练的模型
                if not self.model_manager.load():
                    print("未找到已训练的模型，将使用传统相似度计算方法。可以调用train_model()方法训练模型。")
                    self.use_pytorch = False
                else:
                    print("PyTorch模型加载成功")
            except Exception as e:
                print(f"PyTorch模型初始化失败: {e}，将使用传统方法")
                self.use_pytorch = False
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        if os.path.exists(self.knowledge_base_path):
            try:
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载知识库失败: {e}")
                return self._get_default_knowledge_base()
        else:
            # 如果文件不存在，创建默认知识库
            default_kb = self._get_default_knowledge_base()
            self._save_knowledge_base(default_kb)
            return default_kb
    
    def _save_knowledge_base(self, knowledge_base: Dict):
        """保存知识库到文件"""
        try:
            os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存知识库失败: {e}")
    
    def _get_default_knowledge_base(self) -> Dict:
        """获取默认知识库"""
        return {
            "categories": [
                {
                    "name": "课程安排",
                    "qa_pairs": [
                        {
                            "question": "课程什么时候开始？",
                            "answer": "课程通常在每学期开学第一周开始。具体时间请查看课程表或联系任课教师。",
                            "keywords": ["开始", "时间", "开学", "什么时候"]
                        },
                        {
                            "question": "课程什么时候结束？",
                            "answer": "课程通常在每学期期末前一周结束。具体时间请查看课程表。",
                            "keywords": ["结束", "时间", "期末", "什么时候"]
                        },
                        {
                            "question": "课程的上课时间是什么？",
                            "answer": "课程的上课时间请查看课程表。通常会在选课系统中显示具体的上课时间和地点。",
                            "keywords": ["上课时间", "时间", "课程表", "什么时候上课"]
                        },
                        {
                            "question": "课程在哪里上课？",
                            "answer": "课程的上课地点请查看课程表。通常会在选课系统中显示具体的教室位置。",
                            "keywords": ["地点", "教室", "在哪里", "上课地点"]
                        }
                    ]
                },
                {
                    "name": "作业要求",
                    "qa_pairs": [
                        {
                            "question": "作业什么时候交？",
                            "answer": "作业提交时间请查看课程资料中的作业要求。通常会在课程资料或作业通知中明确说明提交截止时间。",
                            "keywords": ["作业", "提交", "截止", "什么时候交", "交作业"]
                        },
                        {
                            "question": "作业怎么提交？",
                            "answer": "作业通常通过课程平台提交。请登录课程系统，找到对应的作业模块，按照要求上传作业文件。",
                            "keywords": ["作业", "提交", "怎么交", "如何提交", "上传"]
                        },
                        {
                            "question": "作业的格式要求是什么？",
                            "answer": "作业格式要求请查看课程资料中的作业说明。通常包括文件格式（如PDF、Word）、字数要求、格式规范等。",
                            "keywords": ["格式", "要求", "作业格式", "文件格式"]
                        },
                        {
                            "question": "作业可以迟交吗？",
                            "answer": "关于作业迟交政策，请查看课程资料中的作业要求或直接联系任课教师。不同课程可能有不同的政策。",
                            "keywords": ["迟交", "延期", "晚交", "可以迟交"]
                        },
                        {
                            "question": "作业占多少分？",
                            "answer": "作业在总成绩中的占比请查看课程大纲或成绩构成说明。通常会在课程开始时公布。",
                            "keywords": ["分数", "占比", "成绩", "多少分", "权重"]
                        }
                    ]
                },
                {
                    "name": "考试安排",
                    "qa_pairs": [
                        {
                            "question": "什么时候考试？",
                            "answer": "考试时间请查看课程资料中的考试安排通知。通常会在考试前2-3周公布。",
                            "keywords": ["考试", "时间", "什么时候", "考试时间"]
                        },
                        {
                            "question": "考试地点在哪里？",
                            "answer": "考试地点请查看考试安排通知。通常会在考试前公布具体的考场位置。",
                            "keywords": ["考试", "地点", "考场", "在哪里"]
                        },
                        {
                            "question": "考试形式是什么？",
                            "answer": "考试形式（闭卷、开卷、机考等）请查看课程大纲或考试通知。不同课程可能有不同的考试形式。",
                            "keywords": ["考试形式", "闭卷", "开卷", "机考", "形式"]
                        },
                        {
                            "question": "考试范围是什么？",
                            "answer": "考试范围请查看课程资料中的考试大纲或复习资料。通常会在考试前公布。",
                            "keywords": ["考试范围", "范围", "考什么", "复习范围"]
                        }
                    ]
                },
                {
                    "name": "成绩查询",
                    "qa_pairs": [
                        {
                            "question": "怎么查看成绩？",
                            "answer": "成绩可以通过课程系统查看。登录后进入成绩查询模块，即可查看各科成绩。",
                            "keywords": ["成绩", "查看", "查询", "怎么查", "如何查看"]
                        },
                        {
                            "question": "成绩什么时候公布？",
                            "answer": "成绩通常在考试结束后1-2周内公布。具体时间请关注课程通知。",
                            "keywords": ["成绩", "公布", "什么时候", "出成绩"]
                        },
                        {
                            "question": "成绩可以申诉吗？",
                            "answer": "如果对成绩有异议，可以联系任课教师进行申诉。请按照学校规定的申诉流程进行。",
                            "keywords": ["成绩", "申诉", "异议", "可以申诉"]
                        }
                    ]
                },
                {
                    "name": "课程资料",
                    "qa_pairs": [
                        {
                            "question": "在哪里下载课程资料？",
                            "answer": "课程资料可以在课程系统的资料模块中下载。登录后找到对应的课程，进入资料页面即可下载。",
                            "keywords": ["资料", "下载", "在哪里", "课程资料", "课件"]
                        },
                        {
                            "question": "课程资料包括什么？",
                            "answer": "课程资料通常包括课件、讲义、作业要求、参考书目等。具体内容请查看课程资料列表。",
                            "keywords": ["资料", "包括", "内容", "有什么"]
                        }
                    ]
                },
                {
                    "name": "其他问题",
                    "qa_pairs": [
                        {
                            "question": "如何联系老师？",
                            "answer": "可以通过课程系统中的消息功能联系老师，或者查看课程信息中的教师联系方式（邮箱、办公室等）。",
                            "keywords": ["联系", "老师", "教师", "如何联系", "联系方式"]
                        },
                        {
                            "question": "课程有答疑时间吗？",
                            "answer": "课程答疑时间请查看课程信息或课程通知。通常会在课程开始时公布答疑时间和地点。",
                            "keywords": ["答疑", "时间", "答疑时间", "什么时候答疑"]
                        }
                    ]
                }
            ]
        }
    
    def _process_knowledge_base(self) -> List[Dict]:
        """处理知识库，提取所有问答对"""
        processed = []
        for category in self.knowledge_base.get("categories", []):
            for qa_pair in category.get("qa_pairs", []):
                processed.append({
                    "category": category["name"],
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"],
                    "keywords": qa_pair.get("keywords", []),
                    "processed_question": self._preprocess_text(qa_pair["question"]),
                    "processed_question_words": self._preprocess_text(qa_pair["question"], return_list=True),
                    "processed_keywords": [self._preprocess_text(kw) for kw in qa_pair.get("keywords", [])]
                })
        return processed
    
    def _preprocess_text(self, text: str, return_list: bool = False) -> Union[str, List[str]]:
        """
        预处理文本：使用NLTK进行分词、去停用词、词干提取
        
        Args:
            text: 输入文本
            return_list: 是否返回词列表（用于PyTorch模型），否则返回空格分隔的字符串
            
        Returns:
            处理后的文本（字符串或词列表）
        """
        if not text:
            return [] if return_list else ""
        
        # 移除标点符号和特殊字符，保留中英文和数字
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # 使用正则表达式提取中文字符和英文单词
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        # 对于英文，使用NLTK分词
        try:
            english_words = word_tokenize(text.lower())
            # 过滤出纯英文单词
            english_words = [w for w in english_words if w.isalpha() and ord(w[0]) < 128]
        except:
            # 如果NLTK分词失败，使用正则表达式
            english_words = re.findall(r'[a-zA-Z]+', text.lower())
        
        # 合并中文和英文
        all_words = chinese_chars + english_words
        
        # 去停用词
        filtered_words = [
            w for w in all_words 
            if w not in english_stopwords and w not in chinese_stopwords and len(w) > 0
        ]
        
        # 词干提取（仅对英文）
        lemmatized_words = []
        for w in filtered_words:
            if w.isalpha() and ord(w[0]) < 128:  # 英文单词
                try:
                    lemmatized_words.append(lemmatizer.lemmatize(w))
                except:
                    lemmatized_words.append(w)
            else:  # 中文字符
                lemmatized_words.append(w)
        
        if return_list:
            return lemmatized_words
        return ' '.join(lemmatized_words)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        优先使用PyTorch模型，如果不可用则使用余弦相似度
        
        Args:
            text1: 文本1（可以是字符串或词列表）
            text2: 文本2（可以是字符串或词列表）
            
        Returns:
            相似度分数（0-1之间）
        """
        if not text1 or not text2:
            return 0.0
        
        # 如果使用PyTorch模型
        if self.use_pytorch and self.model_manager and self.model_manager.model:
            try:
                # 获取词列表
                if isinstance(text1, str):
                    words1 = text1.split()
                else:
                    words1 = text1
                    
                if isinstance(text2, str):
                    words2 = text2.split()
                else:
                    words2 = text2
                
                # 使用PyTorch模型预测相似度
                similarity = self.model_manager.predict_similarity(words1, words2)
                return float(similarity)
            except Exception as e:
                print(f"PyTorch模型预测失败: {e}，回退到传统方法")
        
        # 传统方法：余弦相似度
        # 确保是字符串格式
        if isinstance(text1, list):
            text1 = ' '.join(text1)
        if isinstance(text2, list):
            text2 = ' '.join(text2)
        
        # 分词
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # 计算词频向量
        all_words = words1.union(words2)
        vector1 = [1 if word in words1 else 0 for word in all_words]
        vector2 = [1 if word in words2 else 0 for word in all_words]
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity
    
    def _calculate_keyword_match_score(self, query: str, keywords: List[str]) -> float:
        """
        计算查询与关键词的匹配分数
        
        Args:
            query: 查询文本
            keywords: 关键词列表
            
        Returns:
            匹配分数（0-1之间）
        """
        if not keywords:
            return 0.0
        
        query_lower = query.lower()
        matches = sum(1 for kw in keywords if kw.lower() in query_lower)
        return matches / len(keywords) if keywords else 0.0
    
    def ask(self, question: str, top_k: int = 3) -> Dict:
        """
        回答问题
        
        Args:
            question: 用户问题
            top_k: 返回前k个最相关的答案
            
        Returns:
            包含答案和相关信息的字典
        """
        if not question or not question.strip():
            return {
                "answer": "抱歉，我没有理解您的问题。请重新提问。",
                "confidence": 0.0,
                "matched_question": None,
                "category": None
            }
        
        # 预处理问题（同时获取字符串和词列表格式）
        processed_question = self._preprocess_text(question)
        processed_question_words = self._preprocess_text(question, return_list=True)
        
        # 计算与所有问答对的相似度
        scores = []
        for qa_pair in self.processed_qa_pairs:
            # 计算文本相似度（使用PyTorch模型或传统方法）
            if self.use_pytorch and self.model_manager and self.model_manager.model:
                # 使用PyTorch模型，传入词列表
                text_similarity = self._calculate_similarity(
                    processed_question_words,
                    qa_pair.get("processed_question_words", qa_pair["processed_question"].split())
                )
            else:
                # 使用传统方法，传入字符串
                text_similarity = self._calculate_similarity(
                    processed_question, 
                    qa_pair["processed_question"]
                )
            
            # 计算关键词匹配分数
            keyword_score = self._calculate_keyword_match_score(
                question, 
                qa_pair["keywords"]
            )
            
            # 综合分数（文本相似度权重0.7，关键词匹配权重0.3）
            combined_score = 0.7 * text_similarity + 0.3 * keyword_score
            
            scores.append({
                "qa_pair": qa_pair,
                "text_similarity": text_similarity,
                "keyword_score": keyword_score,
                "combined_score": combined_score
            })
        
        # 按综合分数排序
        scores.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # 获取最佳匹配
        best_match = scores[0] if scores else None
        
        if best_match and best_match["combined_score"] > 0.3:  # 阈值可调整
            return {
                "answer": best_match["qa_pair"]["answer"],
                "confidence": best_match["combined_score"],
                "matched_question": best_match["qa_pair"]["question"],
                "category": best_match["qa_pair"]["category"],
                "top_matches": [
                    {
                        "question": s["qa_pair"]["question"],
                        "answer": s["qa_pair"]["answer"],
                        "score": s["combined_score"]
                    }
                    for s in scores[:top_k]
                ]
            }
        else:
            return {
                "answer": "抱歉，我没有找到相关答案。请尝试换一种方式提问，或联系任课教师获取帮助。",
                "confidence": best_match["combined_score"] if best_match else 0.0,
                "matched_question": None,
                "category": None,
                "top_matches": []
            }
    
    def add_qa_pair(self, category: str, question: str, answer: str, keywords: List[str] = None):
        """
        添加新的问答对到知识库
        
        Args:
            category: 分类名称
            question: 问题
            answer: 答案
            keywords: 关键词列表
        """
        # 查找或创建分类
        category_found = False
        for cat in self.knowledge_base.get("categories", []):
            if cat["name"] == category:
                cat["qa_pairs"].append({
                    "question": question,
                    "answer": answer,
                    "keywords": keywords or []
                })
                category_found = True
                break
        
        if not category_found:
            # 创建新分类
            if "categories" not in self.knowledge_base:
                self.knowledge_base["categories"] = []
            self.knowledge_base["categories"].append({
                "name": category,
                "qa_pairs": [{
                    "question": question,
                    "answer": answer,
                    "keywords": keywords or []
                }]
            })
        
        # 保存知识库
        self._save_knowledge_base(self.knowledge_base)
        
        # 重新处理知识库
        self.processed_qa_pairs = self._process_knowledge_base()
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return [cat["name"] for cat in self.knowledge_base.get("categories", [])]
    
    def get_qa_pairs_by_category(self, category: str) -> List[Dict]:
        """获取指定分类的所有问答对"""
        for cat in self.knowledge_base.get("categories", []):
            if cat["name"] == category:
                return cat.get("qa_pairs", [])
        return []
    
    def train_model(self, epochs: int = 10, batch_size: int = 32, lr: float = 0.001):
        """
        训练PyTorch模型
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
            lr: 学习率
        """
        if not PYTORCH_AVAILABLE:
            raise ValueError("PyTorch未安装，无法训练模型")
        
        if self.model_manager is None:
            self.model_manager = QAModelManager()
        
        # 准备训练数据
        print("准备训练数据...")
        train_data = []
        
        # 从知识库生成训练数据
        for qa_pair in self.processed_qa_pairs:
            question_words = qa_pair.get("processed_question_words", 
                                        self._preprocess_text(qa_pair["question"], return_list=True))
            
            # 生成正样本（相同问题的相似度为1.0）
            train_data.append((question_words, question_words, 1.0))
            
            # 生成负样本（与其他问题的相似度）
            for other_pair in self.processed_qa_pairs:
                if other_pair["question"] != qa_pair["question"]:
                    other_words = other_pair.get("processed_question_words",
                                                self._preprocess_text(other_pair["question"], return_list=True))
                    # 使用传统方法计算相似度作为标签
                    similarity = self._calculate_similarity(
                        ' '.join(question_words),
                        ' '.join(other_words)
                    )
                    train_data.append((question_words, other_words, similarity))
        
        if len(train_data) < 10:
            raise ValueError("训练数据不足，至少需要10个样本")
        
        print(f"训练数据量: {len(train_data)}")
        
        # 构建词汇表
        all_processed_texts = [qa_pair.get("processed_question_words", 
                                          self._preprocess_text(qa_pair["question"], return_list=True))
                              for qa_pair in self.processed_qa_pairs]
        self.model_manager.build_vocab(all_processed_texts, min_freq=1)
        
        # 创建模型
        self.model_manager.create_model()
        
        # 训练模型
        print("开始训练模型...")
        self.model_manager.train_model(train_data, epochs=epochs, batch_size=batch_size, lr=lr)
        
        # 保存模型
        self.model_manager.save()
        
        # 启用PyTorch模型
        self.use_pytorch = True
        print("模型训练完成并已保存")

