"""
PyTorch文本相似度模型
====================
使用PyTorch构建神经网络模型用于计算文本相似度
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple
import numpy as np
from collections import Counter
import pickle
import os


class TextSimilarityModel(nn.Module):
    """文本相似度神经网络模型"""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 128, hidden_dim: int = 256, num_layers: int = 2):
        """
        初始化模型
        
        Args:
            vocab_size: 词汇表大小
            embedding_dim: 词向量维度
            hidden_dim: 隐藏层维度
            num_layers: LSTM层数
        """
        super(TextSimilarityModel, self).__init__()
        
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        
        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # 双向LSTM编码器
        self.encoder = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.3 if num_layers > 1 else 0
        )
        
        # 注意力机制
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim * 2,
            num_heads=4,
            batch_first=True
        )
        
        # 全连接层
        self.fc1 = nn.Linear(hidden_dim * 2 * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)
        
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, text1: torch.Tensor, text2: torch.Tensor, mask1: torch.Tensor = None, mask2: torch.Tensor = None):
        """
        前向传播
        
        Args:
            text1: 文本1的索引序列 [batch_size, seq_len]
            text2: 文本2的索引序列 [batch_size, seq_len]
            mask1: 文本1的掩码
            mask2: 文本2的掩码
            
        Returns:
            相似度分数 [batch_size, 1]
        """
        # 词嵌入
        emb1 = self.embedding(text1)  # [batch_size, seq_len, embedding_dim]
        emb2 = self.embedding(text2)
        
        # LSTM编码
        lstm_out1, _ = self.encoder(emb1)  # [batch_size, seq_len, hidden_dim * 2]
        lstm_out2, _ = self.encoder(emb2)
        
        # 注意力机制
        attn_out1, _ = self.attention(lstm_out1, lstm_out1, lstm_out1)
        attn_out2, _ = self.attention(lstm_out2, lstm_out2, lstm_out2)
        
        # 池化（使用平均池化）
        if mask1 is not None:
            mask1 = mask1.unsqueeze(-1).float()
            pooled1 = (attn_out1 * mask1).sum(dim=1) / mask1.sum(dim=1)
        else:
            pooled1 = attn_out1.mean(dim=1)
            
        if mask2 is not None:
            mask2 = mask2.unsqueeze(-1).float()
            pooled2 = (attn_out2 * mask2).sum(dim=1) / mask2.sum(dim=1)
        else:
            pooled2 = attn_out2.mean(dim=1)
        
        # 拼接两个文本的表示
        combined = torch.cat([pooled1, pooled2], dim=1)  # [batch_size, hidden_dim * 4]
        
        # 全连接层
        x = F.relu(self.fc1(combined))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.sigmoid(self.fc3(x))  # 输出0-1之间的相似度分数
        
        return x


class Vocabulary:
    """词汇表管理类"""
    
    def __init__(self):
        self.word2idx = {'<PAD>': 0, '<UNK>': 1}
        self.idx2word = {0: '<PAD>', 1: '<UNK>'}
        self.word_count = Counter()
        
    def add_words(self, words: List[str]):
        """添加词汇"""
        for word in words:
            self.word_count[word] += 1
            if word not in self.word2idx:
                idx = len(self.word2idx)
                self.word2idx[word] = idx
                self.idx2word[idx] = word
    
    def build_vocab(self, texts: List[List[str]], min_freq: int = 1):
        """构建词汇表"""
        for text in texts:
            for word in text:
                self.word_count[word] += 1
        
        # 添加满足最小频率的词
        for word, count in self.word_count.items():
            if count >= min_freq and word not in self.word2idx:
                idx = len(self.word2idx)
                self.word2idx[word] = idx
                self.idx2word[idx] = word
    
    def words_to_indices(self, words: List[str], max_len: int = 100) -> List[int]:
        """将词列表转换为索引列表"""
        indices = [self.word2idx.get(word, self.word2idx['<UNK>']) for word in words]
        # 截断或填充
        if len(indices) > max_len:
            indices = indices[:max_len]
        else:
            indices = indices + [self.word2idx['<PAD>']] * (max_len - len(indices))
        return indices
    
    def __len__(self):
        return len(self.word2idx)
    
    def save(self, path: str):
        """保存词汇表"""
        with open(path, 'wb') as f:
            pickle.dump({
                'word2idx': self.word2idx,
                'idx2word': self.idx2word,
                'word_count': dict(self.word_count)
            }, f)
    
    @classmethod
    def load(cls, path: str):
        """加载词汇表"""
        vocab = cls()
        with open(path, 'rb') as f:
            data = pickle.load(f)
            vocab.word2idx = data['word2idx']
            vocab.idx2word = data['idx2word']
            vocab.word_count = Counter(data['word_count'])
        return vocab


class QAModelManager:
    """QA模型管理器"""
    
    def __init__(self, model_dir: str = None):
        """
        初始化模型管理器
        
        Args:
            model_dir: 模型保存目录
        """
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(base_dir, 'app', 'models', 'qa_model')
        
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.vocab = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_seq_len = 100
        
    def build_vocab(self, processed_texts: List[List[str]], min_freq: int = 1):
        """构建词汇表"""
        self.vocab = Vocabulary()
        self.vocab.build_vocab(processed_texts, min_freq=min_freq)
        print(f"词汇表大小: {len(self.vocab)}")
    
    def create_model(self, embedding_dim: int = 128, hidden_dim: int = 256, num_layers: int = 2):
        """创建模型"""
        if self.vocab is None:
            raise ValueError("请先构建词汇表")
        
        self.model = TextSimilarityModel(
            vocab_size=len(self.vocab),
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers
        ).to(self.device)
        
        return self.model
    
    def train_model(self, train_data: List[Tuple[List[str], List[str], float]], 
                   epochs: int = 10, batch_size: int = 32, lr: float = 0.001):
        """
        训练模型
        
        Args:
            train_data: 训练数据，格式为 [(text1_words, text2_words, similarity_score), ...]
            epochs: 训练轮数
            batch_size: 批次大小
            lr: 学习率
        """
        if self.model is None:
            raise ValueError("请先创建模型")
        
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        for epoch in range(epochs):
            total_loss = 0
            # 打乱数据
            np.random.shuffle(train_data)
            
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i + batch_size]
                
                # 准备批次数据
                text1_batch = []
                text2_batch = []
                labels = []
                
                for text1_words, text2_words, label in batch:
                    indices1 = self.vocab.words_to_indices(text1_words, self.max_seq_len)
                    indices2 = self.vocab.words_to_indices(text2_words, self.max_seq_len)
                    text1_batch.append(indices1)
                    text2_batch.append(indices2)
                    labels.append(label)
                
                text1_tensor = torch.LongTensor(text1_batch).to(self.device)
                text2_tensor = torch.LongTensor(text2_batch).to(self.device)
                label_tensor = torch.FloatTensor(labels).unsqueeze(1).to(self.device)
                
                # 前向传播
                optimizer.zero_grad()
                output = self.model(text1_tensor, text2_tensor)
                loss = criterion(output, label_tensor)
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / (len(train_data) // batch_size + 1)
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
    
    def predict_similarity(self, text1_words: List[str], text2_words: List[str]) -> float:
        """
        预测两个文本的相似度
        
        Args:
            text1_words: 文本1的词列表
            text2_words: 文本2的词列表
            
        Returns:
            相似度分数 (0-1)
        """
        if self.model is None:
            raise ValueError("模型未加载")
        
        self.model.eval()
        with torch.no_grad():
            indices1 = self.vocab.words_to_indices(text1_words, self.max_seq_len)
            indices2 = self.vocab.words_to_indices(text2_words, self.max_seq_len)
            
            text1_tensor = torch.LongTensor([indices1]).to(self.device)
            text2_tensor = torch.LongTensor([indices2]).to(self.device)
            
            output = self.model(text1_tensor, text2_tensor)
            return output.item()
    
    def save(self, model_name: str = 'qa_model'):
        """保存模型和词汇表"""
        if self.model is None or self.vocab is None:
            raise ValueError("模型或词汇表未初始化")
        
        model_path = os.path.join(self.model_dir, f'{model_name}.pth')
        vocab_path = os.path.join(self.model_dir, f'{model_name}_vocab.pkl')
        
        torch.save(self.model.state_dict(), model_path)
        self.vocab.save(vocab_path)
        print(f"模型已保存到: {model_path}")
        print(f"词汇表已保存到: {vocab_path}")
    
    def load(self, model_name: str = 'qa_model', embedding_dim: int = 128, 
             hidden_dim: int = 256, num_layers: int = 2):
        """加载模型和词汇表"""
        vocab_path = os.path.join(self.model_dir, f'{model_name}_vocab.pkl')
        model_path = os.path.join(self.model_dir, f'{model_name}.pth')
        
        if not os.path.exists(vocab_path) or not os.path.exists(model_path):
            return False
        
        # 加载词汇表
        self.vocab = Vocabulary.load(vocab_path)
        
        # 创建并加载模型
        self.model = TextSimilarityModel(
            vocab_size=len(self.vocab),
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers
        ).to(self.device)
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        print(f"模型已从 {model_path} 加载")
        return True

