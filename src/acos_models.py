"""Syntax-Aware Deep Neural Network for Aspect-Category-Opinion-Sentiment (ACOS)
Quadruple Mining and Implicit Opinion Disentanglement.

Implements SyntaxAwareACOSNet:
- Multi-channel input: Word embeddings + POS tags + Syntactic Dependency relation embeddings + SDP distance
- Syntax-Guided BiLSTM-GCN Feature Layer
- Multi-Task Prediction Heads:
  1. Aspect Span BIO Sequence Tagger
  2. Opinion Span BIO Sequence Tagger
  3. Aspect Category Classifier (9 classes)
  4. Sentiment Polarity Classifier (3 classes)
  5. Implicit vs. Explicit Opinion Disentanglement Head (Binary)
"""

from __future__ import annotations
import math
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

CATEGORIES = [
    "FOOD#QUALITY",
    "FOOD#PRICES",
    "FOOD#STYLE_OPTIONS",
    "SERVICE#GENERAL",
    "SERVICE#PROMPTNESS",
    "AMBIENCE#GENERAL",
    "RESTAURANT#PRICES",
    "HYGIENE#CLEANLINESS",
    "HYGIENE#FOOD_SAFETY"
]

POLARITIES = ["positive", "neutral", "negative"]
OPINION_TYPES = ["explicit", "implicit"]

# Vocabulary Mappings
POS_TAGS = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "PROPN", "DET", "ADP", "NUM", "PUNCT", "CCONJ", "AUX", "OTHER"]
DEP_TAGS = ["ROOT", "nsubj", "amod", "dobj", "pobj", "acomp", "advmod", "prep", "conj", "neg", "attr", "compound", "det", "OTHER"]

class Vocabulary:
    def __init__(self, min_freq: int = 1):
        self.word2idx = {"<PAD>": 0, "<UNK>": 1}
        self.idx2word = {0: "<PAD>", 1: "<UNK>"}
        self.min_freq = min_freq
        self.pos2idx = {p: i for i, p in enumerate(POS_TAGS)}
        self.dep2idx = {d: i for i, d in enumerate(DEP_TAGS)}

    def build_vocab(self, texts: List[str]):
        counts = {}
        for text in texts:
            for token in text.lower().split():
                counts[token] = counts.get(token, 0) + 1
        for token, count in counts.items():
            if count >= self.min_freq and token not in self.word2idx:
                idx = len(self.word2idx)
                self.word2idx[token] = idx
                self.idx2word[idx] = token

    def encode_words(self, words: List[str]) -> List[int]:
        return [self.word2idx.get(w.lower(), 1) for w in words]

    def encode_pos(self, pos_tags: List[str]) -> List[int]:
        return [self.pos2idx.get(p, len(POS_TAGS) - 1) for p in pos_tags]

    def encode_deps(self, dep_tags: List[str]) -> List[int]:
        return [self.dep2idx.get(d, len(DEP_TAGS) - 1) for d in dep_tags]


class SyntaxAwareACOSNet(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        word_dim: int = 128,
        pos_dim: int = 32,
        dep_dim: int = 32,
        hidden_dim: int = 128,
        num_categories: int = len(CATEGORIES),
        num_polarities: int = len(POLARITIES),
        dropout: float = 0.3
    ):
        super().__init__()
        self.word_embedding = nn.Embedding(vocab_size, word_dim, padding_idx=0)
        self.pos_embedding = nn.Embedding(len(POS_TAGS), pos_dim)
        self.dep_embedding = nn.Embedding(len(DEP_TAGS), dep_dim)

        total_input_dim = word_dim + pos_dim + dep_dim

        # BiLSTM Encoder
        self.bilstm = nn.LSTM(
            total_input_dim,
            hidden_dim // 2,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if dropout > 0 else 0
        )

        # Syntactic Self-Attention Layer (Guided by Dependency Graph)
        self.syntax_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=4,
            dropout=dropout,
            batch_first=True
        )

        # Multi-Task Prediction Heads
        # 1. Aspect BIO Tagging: B-ASP (1), I-ASP (2), O (0)
        self.aspect_head = nn.Linear(hidden_dim, 3)

        # 2. Opinion BIO Tagging: B-OP (1), I-OP (2), O (0)
        self.opinion_head = nn.Linear(hidden_dim, 3)

        # Pooled Representation for Sentence-Level Category & Sentiment
        self.pooler = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh()
        )

        # 3. Category Classifier (9 classes)
        self.category_head = nn.Linear(hidden_dim, num_categories)

        # 4. Sentiment Classifier (3 classes)
        self.sentiment_head = nn.Linear(hidden_dim, num_polarities)

        # 5. Implicit vs. Explicit Disentanglement Head (Binary: 0=Explicit, 1=Implicit)
        self.implicit_head = nn.Linear(hidden_dim, 1)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        word_ids: torch.Tensor,
        pos_ids: torch.Tensor,
        dep_ids: torch.Tensor,
        adj_matrix: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """Forward pass.
        Args:
            word_ids: (batch_size, seq_len)
            pos_ids: (batch_size, seq_len)
            dep_ids: (batch_size, seq_len)
            adj_matrix: (batch_size, seq_len, seq_len) syntactic graph adjacency
        """
        # Embeddings
        w_emb = self.word_embedding(word_ids)
        p_emb = self.pos_embedding(pos_ids)
        d_emb = self.dep_embedding(dep_ids)

        inputs = torch.cat([w_emb, p_emb, d_emb], dim=-1)
        inputs = self.dropout(inputs)

        # BiLSTM Contextualization
        lstm_out, _ = self.bilstm(inputs)

        # Syntax Graph Attention
        if adj_matrix is not None:
            # Mask non-syntactic relations with attention weights
            # Ensure diagonal has self-loops so no row is completely masked (avoids NaNs)
            batch_sz, seq_l, _ = adj_matrix.shape
            eye = torch.eye(seq_l, device=adj_matrix.device, dtype=adj_matrix.dtype).unsqueeze(0).expand(batch_sz, -1, -1)
            adj_with_self = torch.clamp(adj_matrix + eye, max=1.0)
            
            # MultiheadAttention requires (batch_size * num_heads, seq_len, seq_len)
            attn_mask = (adj_with_self == 0).repeat_interleave(self.syntax_attention.num_heads, dim=0)
            syntax_out, _ = self.syntax_attention(lstm_out, lstm_out, lstm_out, attn_mask=attn_mask)
            fused = lstm_out + self.dropout(syntax_out)
        else:
            syntax_out, _ = self.syntax_attention(lstm_out, lstm_out, lstm_out)
            fused = lstm_out + self.dropout(syntax_out)

        # Token-Level Predictions
        aspect_logits = self.aspect_head(fused)       # (batch, seq_len, 3)
        opinion_logits = self.opinion_head(fused)     # (batch, seq_len, 3)

        # Global Sentence Representation (mean pooling over non-pad tokens)
        pad_mask = (word_ids != 0).unsqueeze(-1).float()
        pooled = (fused * pad_mask).sum(dim=1) / (pad_mask.sum(dim=1) + 1e-8)
        pooled = self.pooler(pooled)

        category_logits = self.category_head(pooled)   # (batch, num_categories)
        sentiment_logits = self.sentiment_head(pooled) # (batch, num_polarities)
        implicit_logits = self.implicit_head(pooled)   # (batch, 1)

        return {
            "aspect_logits": aspect_logits,
            "opinion_logits": opinion_logits,
            "category_logits": category_logits,
            "sentiment_logits": sentiment_logits,
            "implicit_logits": implicit_logits
        }
